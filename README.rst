pmxc
====

Install on Debian
+++++++++++++

.. code:: bash

    sudo apt install python3-pip python-virtualenv git
    virtualenv -p /usr/bin/python3 --no-site-packages venv
    source venv/bin/activate
    pip install -e ."[performance,uvloop]"


Install on Windows
++++++++++++++++++

- Install babu from http://babun.github.io/
- launch %HOMEPATH%/.babun/update.bat
- Run babu

.. code:: bash

    $ pact install python3 python3-pip python3-devel

    # Must point to /usr/bin/python3 if not uninstall python from Windows and reboot
    $ which python3

    $ git clone https://github.com/pcdummy/pmxc.git
    $ cd pmxc
    $ pip3 install -e .

- Optional install "virt-viewer": https://virt-manager.org/download/sources/virt-viewer/virt-viewer-x64-6.0.msi
- Optional install "tightvnc": https://www.tightvnc.com/download.php


The version parts
+++++++++++++++++

The first 2 numbers are the Promox VE API pmxc targets to, the next 2 are the pmxc version.

Like 5.2.0.1 means its target for Promox VE 5.2 and its the first release (0.1) for that.

Development
+++++++++++

Linux
-----

.. code:: bash

    $ pip install -e ."[development,performance,uvloop]"

Windows
-------

.. code:: bash

    $ pip install -e ."[development,performance]"

License
+++++++

MIT


Copyright
+++++++++

Copyright (c) 2018 by René Jochum