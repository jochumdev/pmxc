import asyncio
from os import get_terminal_size
import sys
from functools import partial

import aiohttp


class WSTerminal(object):
    def __init__(self, loop, ws, user, ticket, *, terminal=None):
        self._loop = loop
        self._ws = ws
        self._user = user
        self._ticket = ticket

        if (terminal is not None and ('size' not in terminal or 'stdin' not in terminal or 'stdout' not in terminal)):
            raise ValueError('Invalid terminal dict received')

        if (terminal is not None):
            self._provided_termrw = True
            self._size = terminal['size']
            self._stdin = terminal['stdin']
            self._stdout = terminal['stdout']
        else:
            self._provided_termrw = False
            self._size = get_terminal_size(sys.stdout.fileno())
            self._stdin = sys.stdin
            self._stdout = sys.stdout

        self._ws_ready = False
        self._closed = False
        self._tasks = []

    async def run(self):
        # Start tasks
        self._tasks.append(asyncio.Task(self._ping_websocket()))
        self._tasks.append(asyncio.Task(self._check_resize()))

        # Start ws and terminal loop
        await asyncio.wait([self._read_websocket(), self._read_terminal()])

        # Stop all tasks
        for task in self._tasks:
            task.cancel()


    async def resize(self, columns, rows):
        if self._closed:
            return False

        # Already send that size
        if self._size[0] == columns and self._size[1] == rows:
            return True

        self._size = (columns, rows,)
        message = "1:" + str(self._size[0]) + ":" + str(self._size[1]) + ":"
        message = str.encode(message)
        await self._ws.send_bytes(message)

    async def _check_resize(self):
        if self._provided_termrw:
            return

        while True:
            await asyncio.sleep(1)
            if self._closed:
                break

            if not self._ws_ready:
                continue

            await self.resize(*get_terminal_size(sys.stdout.fileno()))

    async def _ping_websocket(self):
        while True:
            await asyncio.sleep(3)
            if self._closed:
                break

            if not self._ws_ready:
                continue

            message = str.encode("2")
            await self._ws.send_bytes(message)

    async def _read_websocket(self):
        #
        # Auth (again)
        #
        message = self._user + ":" + self._ticket + "\n"
        message = str.encode(message)
        await self._ws.send_bytes(message)

        #
        # Resize message
        #
        message = "1:" + str(self._size[0]) + ":" + str(self._size[1]) + ":"
        message = str.encode(message)
        await self._ws.send_bytes(message)
        del(message)

        self._ws_ready = True

        try:
            async for msg in self._ws:
                await asyncio.sleep(0)

                if self._closed:
                    break

                if msg.type == aiohttp.WSMsgType.BINARY:
                    message = msg.data.decode('utf8')
                    if message == 'OK':
                        continue

                    await self._loop.run_in_executor(None, partial(self._stdout.write, message))
                    await self._loop.run_in_executor(None, self._stdout.flush)

                elif msg.type == aiohttp.WSMsgType.CLOSED:
                    self._closed = True
                    break

                elif msg.type == aiohttp.WSMsgType.ERROR:
                    self._closed = True
                    break
        finally:
            self._closed = True

    async def _read_terminal(self):
        try:
            if not self._provided_termrw:
                p = await asyncio.create_subprocess_exec('stty', 'raw', '-echo')
                await p.communicate()

            ctrl_a_pressed_before = False
            while True:
                if self._closed:
                    break

                await asyncio.sleep(0)

                char = await self._loop.run_in_executor(None, partial(self._stdin.read, 1))

                num = ord(char)
                if ctrl_a_pressed_before and num == int("0x71", 16):
                    await self._ws.close()
                    self._closed = True
                    break

                if num == int("0x01", 16):
                    ctrl_a_pressed_before = not ctrl_a_pressed_before
                else:
                    ctrl_a_pressed_before = False

                message = "0:" + str(len(char)) + ":" + char
                await self._ws.send_bytes(str.encode(message))

        except Exception as e:
            print(e)

        finally:
            if not self._provided_termrw:
                p = await asyncio.create_subprocess_exec('stty', 'sane')
                await p.communicate()
