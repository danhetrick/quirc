# Quirc
A Python/Qt5 IRC client
## Requirements
**Quirc** requires Python 3, Twisted, and Qt5. Installing the requirements is as easy and opening a terminal and executing:

    pip install pyqt5
    pip install Twisted

If you want to use SSL to connect to IRC, pyOpenSSL and service_identity is also required:

    pip install pyOpenSSL
    pip install service_identity

If pyOpenSSL is not installed, SSL connections will not be possible; only commands to connect to normal, non-encrypted connections will be shown.

**Quirc** was written and tested under Windows, and should run in any other OS that supports Python 3, Qt5, and Twisted.

## Usage
**Quirc** is a single channel IRC client. It takes no mandatory command-line arguments. Once **Quirc** is up and running, use the `/connect` command to connect to an IRC server. Optional command-line options are available:

    -h, --help			Display usage text
    -n, --nick NICKNAME		Set nickname (default: quirc)
    -u, --username USERNAME		Set username (default: quirc)
    -c, --channel CHANNEL		Set initial channel (default: #quirc)
    -d, --default CHANNEL		Set default channel (default: #quirc)
    -p, --password KEY              Key required to join channel
    -f, --font FONT			Set display font (default: "Courier New")
    -C, --highcontrast      Quirc will use a high contrast color set

Once up and running, **Quirc** runs like any other graphical IRC client you might have used.

## Quirc Client Commands

    /connect SERVER PORT    Connects to an IRC server
    /ssl SERVER PORT        Connects to an IRC server via SSL (requires pyOpenSSL)
    /nick NICKNAME          Changes the client's nickname
    /msg TARGET MESSAGE     Sends a private or channel message
    /me ACTION              Sends a CTCP action message
    /join CHANNEL [KEY]     Joins a new channel, and leaves the current one
    /away [MESSAGE]         Sets status to "away"
    /back                   Sets status to "back"
    /invite NICK CHANNEL    Invites a user to a channel
    /whois USER             Request WHOIS information from the server
    /raw MESSAGE            Sends an unaltered message to the IRC server
    /quit [MESSAGE]         Disconnects from IRC server
    /exit                   Disconnects from IRC server and exits **Quirc**

If the client has operator status, there are three more commands available:

    /topic TEXT             Sets the channel's topic
    /key TEXT               Sets the channel's key
    /nokey                  Removes a channel's key

Right clicking on the user list will show a menu with available commands, as will right clicking on the channel name (at the top right of the window) or the topic display (at the top left).

## Quirc Gadget

**Quirc** can also be ran as a "gadget" (like the discontinued [Windows Desktop Gadgets](https://en.wikipedia.org/wiki/Windows_Desktop_Gadgets)). The application will run without a window title and border, and it will not appear in the task manager; the window can't be moved with the mouse. Optionally, the gadget can appear on top of all other windows, or normally. These command-line arguments are used to configure the **Quirc** gadget:

    -g, --gadget            Run Quirc as a gadget
    -x NUMBER               Gadget's X location
    -y NUMBER               Gadget's Y location
    -w, --width NUMBER      Gadget's width
    -H, --height NUMBER     Gadget's height
    -t, --ontop             Gadget will always be on top of other windows

When running as a gadget, **Quirc** adds a couple of client commands to change the gadget at runtime:

    /move X_VALUE Y_VALUE   Moves the Quirc gadget
    /size WIDTH HEIGHT      Resizes the Quirc gadget

To close the gadget, use the `/exit` command.

## Example Quirc Usage

![Quirc Usage](https://github.com/danhetrick/quirc/blob/master/quirc_usage.gif?raw=true)
