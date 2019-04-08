# Quirc
A open source Python3/Qt5 IRC client. The latest version is **0.22**.

**Quirc** is being actively developed. Although it is missing some features, it is functional at the moment, and can be used for chatting.

## Requirements
**Quirc** requires Python 3, Qt5, and a few modules. Installing the requirements is as easy and opening a terminal and executing:

    pip install pyqt5
    pip install Twisted
    pip install qt5reactor

If you want to use SSL to connect to IRC, pyOpenSSL and service_identity is also required:

    pip install pyOpenSSL
    pip install service_identity

If pyOpenSSL is not installed, SSL connections will not be possible; only commands to connect to normal, non-encrypted connections will be shown.

**Quirc** was written and tested under Windows, and should run in any other OS that supports Python 3 and Qt5.

## Developing **Quirc**

Note: *All development for Quirc is done on Windows. There is no reason why it shouldn't run on any non-Windows operating system, but this is untested. All scripts included for development will run only on Windows, by design.*

It's written in Python, so it doesn't really need to be "built". I've included a script in the root directory, `make_dist.py`, which will build a zip file with all the files you need to run Quirc; when ran, it will create a zip file named `quirc-0.22.zip` which contains all the scripts and other files needed to run, minus any of the developer cruft.

The batch file in the root directory, `compile_resources.bat`, bundles all the images in `/resources` into a single file, `/quirc/resources.py`.

## Usage
**Quirc** is a single server IRC client. It uses a multiple document interface (MDI), much like popular Windows IRC client mIRC.

