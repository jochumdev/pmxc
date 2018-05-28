pmxc
====

Install on *nix
+++++++++++++++



Install on Windows
++++++++++++++++++

1.) Install babu from http://babun.github.io/
2.) launch %HOMEPATH%/.babun/update.bat
3.) Run babu

... code:: bash

    $ pact install python3 python3-pip

    # Must point to /usr/bin/python3 if not uninstall python from Windows and reboot
    $ which python3

    $ git clone https://github.com/pcdummy/pmxc.git
    $ cd pmxc
    $ pip3 install -e .

4.) Optional install "virt-viewer": https://virt-manager.org/download/sources/virt-viewer/virt-viewer-x64-6.0.msi
5.) Optional install "tightvnc": https://www.tightvnc.com/download.php


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

... code:: bash

    $ pip install -e ."[development,performance]"

License
+++++++

MIT


Copyright
+++++++++

Copyright (c) 2018 by René Jochum