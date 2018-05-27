class Resource(object):
    def __init__(self, conn, path):
        self._conn = conn
        self._path = path

    def url_join(self, *args):
        if not args:
            return self

        path = self._path + '/' + '/'.join(args)
        return Resource(self._conn, path)

    def __getattr__(self, item):
        if item.startswith('_'):
            raise AttributeError(item)

        return self.url_join(item)

    def __call__(self, args):
        if not args:
            return self

        if not isinstance(args, (tuple, list)):
            args = [str(args)]

        return self.url_join(*args)

    @property
    def path(self):
        return self._path

    @property
    def conn(self):
        return self._conn

    async def get(self, *args, **params):
        json = await self(args).request2('GET', **params)
        return json['data']

    async def post(self, *args, **params):
        json = await self(args).request2('POST', **params)
        return json['data']

    async def put(self, *args, **params):
        json = await self(args).request2('PUT', **params)
        return json['data']

    async def delete(self, *args, **params):
        json = await self(args).request2('DELETE', **params)
        return json['data']

    async def options(self, *args, **params):
        json = await self(args).request2('OPTIONS', **params)
        return json['data']

    async def request(self, *args, method, **params):
        return await self(args).request2(method, **params)

    async def request2(self, method, **params):
        return await self._conn.request(method, self._path, **params)
