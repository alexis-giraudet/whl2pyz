# whl2pyz
Generate Python executable zip archive for each entry point from wheel packages.

## Installation

```sh
python3 -m pip install whl2pyz
```

## Usage and Examples

Print usage:
```sh
$ whl2pyz --help
usage: whl2pyz [-h] [-w [WHEELS ...]] [-o OUTDIR] [-p PYTHON] [-c] [-x] [pip_args ...]

Generate Python executable zip archive for each entry point from wheel packages (requires pip module).

positional arguments:
  pip_args              Extra pip install arguments.

options:
  -h, --help            show this help message and exit
  -w [WHEELS ...], --wheels [WHEELS ...]
                        Install given wheels to the Python executable zip archive and use only entry points from [WHEEL].dist-info/entry_points.txt.
  -o OUTDIR, --outdir OUTDIR
                        The output directory where Python executable zip archives (.pyz) are generated (default is ./bin).
  -p PYTHON, --python PYTHON
                        The name of the Python interpreter to use (default: no shebang line). Use "/usr/bin/env python3" to make the application directly executable on POSIX
  -c, --compress        Compress files with the deflate method. Files are stored uncompressed by default.
  -x, --auto-extract    The Python executable zip archive will be extracted into a temporary directory and run on the file system to allow execution of binary packages including a C
                        extension.
```

Packaging [nvitop](https://pypi.org/project/nvitop/) in a zip app:
```sh
$ whl2pyz -x -p "/usr/bin/env python3" -- nvitop
...
$ ./bin/nvitop.pyz
...
```

Packaging standalone (no backend) [PyVISA](https://pypi.org/project/PyVISA/) in a portable zip app:
```sh
$ whl2pyz -p "/usr/bin/env python3" -- pyvisa
...
$ ./bin/pyvisa-info.pyz 
Machine Details:
   Platform ID:    Linux-6.8.0-58-generic-x86_64-with-glibc2.35
   Processor:      x86_64

Python:
   Implementation: CPython
   Executable:     python3
   Version:        3.10.12
   Compiler:       GCC 11.4.0
   Architecture:   ('x86', 64)
   Build:          Feb  4 2025 14:57:36 (#main)
   Unicode:        UCS4

PyVISA Version: 1.15.0

Backends:
   ivi:
      Version: 1.15.0 (bundled with PyVISA)
      Binary library: Not found
$ ./bin/pyvisa-shell.pyz
...
```

Packaging [PyVISA](https://pypi.org/project/PyVISA/) with [PyVISA-py](https://pypi.org/project/PyVISA-py/) backend in a portable zip app:
```sh
$ whl2pyz -p "/usr/bin/env python3" -- pyvisa pyvisa-py
...
$ ./bin/pyvisa-info.pyz 
Machine Details:
   Platform ID:    Linux-6.8.0-58-generic-x86_64-with-glibc2.35
   Processor:      x86_64

Python:
   Implementation: CPython
   Executable:     python3
   Version:        3.10.12
   Compiler:       GCC 11.4.0
   Architecture:   ('x86', 64)
   Build:          Feb  4 2025 14:57:36 (#main)
   Unicode:        UCS4

PyVISA Version: 1.15.0

Backends:
   ivi:
      Version: 1.15.0 (bundled with PyVISA)
      Binary library: Not found
   py:
      Version: 0.8.0
      TCPIP INSTR: Available 
         Resource discovery:
         - VXI-11: partial (psutil not installed)
         - hislip: disabled (zeroconf not installed)
      TCPIP SOCKET: Available 
      PRLGX_TCPIP INTFC: Available 
      GPIB INSTR: Available 
      ASRL INSTR:
         Please install PySerial (>=3.0) to use this resource type.
         No module named 'serial'
      USB INSTR:
         Please install PyUSB to use this resource type.
         No module named 'usb'
      USB RAW:
         Please install PyUSB to use this resource type.
         No module named 'usb'
      VICP INSTR:
         Please install PyVICP to use this resource type.
      PRLGX_ASRL INTFC:
         Please install PySerial (>=3.0) to use this resource type.
         No module named 'serial'
      GPIB INTFC:
         Please install linux-gpib (Linux) or gpib-ctypes (Windows, Linux) to use this resource type. Note that installing gpib-ctypes will give you access to a broader range of functionalities.
         No module named 'gpib'
$ ./bin/pyvisa-shell.pyz
...
```

Packaging [PyVISA](https://pypi.org/project/PyVISA/) with [PyVISA-py](https://pypi.org/project/PyVISA-py/) backend including optional dependencies in a zip app:
```sh
$ whl2pyz -x -p "/usr/bin/env python3" -- pyvisa pyvisa-py[serial,usb,psutil,hislip-discovery]
...
$ ./bin/pyvisa-info.pyz 
Machine Details:
   Platform ID:    Linux-6.8.0-58-generic-x86_64-with-glibc2.35
   Processor:      x86_64

Python:
   Implementation: CPython
   Executable:     python3
   Version:        3.10.12
   Compiler:       GCC 11.4.0
   Architecture:   ('x86', 64)
   Build:          Feb  4 2025 14:57:36 (#main)
   Unicode:        UCS4

PyVISA Version: 1.15.0

Backends:
   ivi:
      Version: 1.15.0 (bundled with PyVISA)
      Binary library: Not found
   py:
      Version: 0.8.0
      ASRL INSTR: Available via PySerial (3.5)
      USB INSTR: Available via PyUSB (1.3.1). Backend: libusb1
      USB RAW: Available via PyUSB (1.3.1). Backend: libusb1
      TCPIP INSTR: Available 
         Resource discovery:
         - VXI-11: ok
         - hislip: ok
      TCPIP SOCKET: Available 
      PRLGX_TCPIP INTFC: Available 
      PRLGX_ASRL INTFC: Available via PySerial (3.5)
      GPIB INSTR: Available 
      VICP INSTR:
         Please install PyVICP to use this resource type.
      GPIB INTFC:
         Please install linux-gpib (Linux) or gpib-ctypes (Windows, Linux) to use this resource type. Note that installing gpib-ctypes will give you access to a broader range of functionalities.
         No module named 'gpib'
$ ./bin/pyvisa-shell.pyz
...
```
