# Quirc
A Python/Qt5 IRC client
## Requirements
**Quirc** requires Python 3, Twisted, and Qt5. Installing the requirements is as easy and opening a terminal and executing:

    pip install pyqt5
    pip install Twisted

**Quirc** was written and tested under Windows, and should run in any other OS that supports Python 3, Qt5, and Twisted.

## Usage
**Quirc** is a single channel IRC client. It takes two required command-line arguments, the server and port of the IRC server to connect to. So, to connect to EFnet, you could use:

    python quirc.py irc.servercentral.net 6667
When executed, **Quirc** will connect to the IRC server automatically, and join the default channel, `#quirc`, once connected. To change what channel to join on connection, and a whole bunch of other stuff, use command-line options:

    -h, --help			Display usage text
    -n, --nick NICKNAME		Set nickname (default: quirc)
    -u, --username USERNAME		Set username (default: quirc)
    -c, --channel CHANNEL		Set initial channel (default: #quirc)
    -d, --default CHANNEL		Set default channel (default: #quirc)
    -p, --password KEY              Key required to join channel
    -C, --chat COLOR		Set chat display color (default: blue)
    -P, --private COLOR		Set private message color (default: red)
    -s, --system COLOR		Set system message color (default: grey)
    -a, --action COLOR		Set CTCP action message color (default: green)
    -N, --notice COLOR		Set notice message color (default: purple)
    -f, --font FONT			Set display font (default: "Courier New")

Once up and running, **Quirc** runs like any other graphical IRC client you might have used.  Enter `/help` for a list of commands.

![Quirc Usage](https://github.com/danhetrick/quirc/blob/master/quirc_usage.gif?raw=true)
