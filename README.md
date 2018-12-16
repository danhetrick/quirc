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

For a more complex example, let's connect to EFnet, use the nickname `bob`, join channel `#foo`, use "Arial" as the display font, and use the color orange for all system messages:

```bash
python quirc.py irc.servercentral.net 6667 -n bob --channel "#foo" --font "Arial" -s "orange"
```

Once up and running, **Quirc** runs like any other graphical IRC client you might have used.

## Quirc Client Commands

    /nick NICKNAME          Changes the client's nickname
    /msg TARGET MESSAGE     Sends a private or channel message
    /me ACTION              Sends a CTCP action message
    /join CHANNEL [KEY]     Joins a new channel, and leaves the current one
    /away [MESSAGE]         Sets status to "away"
    /back                   Sets status to "back"
    /invite NICK CHANNEL    Invites a user to a channel
    /raw MESSAGE            Sends an unaltered message to the IRC server
    /quit [MESSAGE]         Disconnects from IRC and quits

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

To close the gadget, use the `/quit` command.

## Example Quirc Usage

![Quirc Usage](https://github.com/danhetrick/quirc/blob/master/quirc_usage.gif?raw=true)
