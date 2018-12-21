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
    -C, --highcontrast              Quirc will use a high contrast color set
    -l, --nolinks               Turn off URL detection in chat
    -m, --maxlength NUMBER      Sets the maximum size of sent messages (default:450)
    -s, --script FILENAME       Sets a script to execute on start

Once up and running, **Quirc** runs like any other graphical IRC client you might have used.

## Quirc Client Commands

    /connect SERVER PORT    Connects to an IRC server
    /ssl SERVER PORT        Connects to an IRC server via SSL (requires pyOpenSSL)
    /script [FILENAME]      Loads a list of commands from a file and executes them
    /var NAME VALUE         Creates a script variable
    /delay TIME COMMAND     Delays the execution of a command by TIME seconds
    /nick NICKNAME          Changes the client's nickname
    /msg TARGET MESSAGE     Sends a private or channel message
    /me ACTION              Sends a CTCP action message
    /join CHANNEL [KEY]     Joins a new channel, and leaves the current one
    /mode TARGET MODE ARGS  Sets a channel or user mode
    /oper USER PASSWORD     Logs into an IRCop account
    /list [CHANNEL] [...]   Requests channel list information
    /away [MESSAGE]         Sets status to "away"
    /back                   Sets status to "back"
    /invite NICK CHANNEL    Invites a user to a channel
    /whois USER             Request WHOIS information from the server
    /whowas USER            Requests WHOWAS information from the server
    /who TERMS              Search for users
    /time                   Requests the server's date/time
    /version                Requests the server's software version
    /info                   Requests the server's info text
    /raw MESSAGE            Sends an unaltered message to the IRC server
    /quit [MESSAGE]         Disconnects from IRC server
    /exit                   Disconnects from IRC server and exits Quirc

If the client has operator status, there are three more commands available:

    /topic TEXT             Sets the channel's topic
    /key TEXT               Sets the channel's key
    /nokey                  Removes a channel's key

Right clicking on the user list will show a menu with available commands, as will right clicking on the channel name (at the top right of the window) or the topic display (at the top left).

Commands can contain "variables". To inject client information into commands, use the following:

    $server         The hostname of the server currently connected to
    $port           The server port connected to
    $uptime         The client uptime
    $channel        The client's current channel
    $nickname       The client's current nickname

Variable names are case-insensitive. A reference to "$server" is the same as a reference to "$SERVER" is the same as a reference to "$sErVeR".

Multiple commands can be issued at once by chaining them together with "&&". For example, to join channel #foo, say hello, and leave the channel and join #bar, you could use:

```
/join #foo && /msg #foo Hello, everybody! && /join #bar
```

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

## Quirc Scripting

The `/script` command can load a list of commands from a text file.  If the `/script` command is issued without any arguments, a "file open" dialog is used to get a file name to load; the client input is then set to `/script` with the file name. Hit enter to execute the script.

Commands *must* be entered as you would in the client; that is, each command begins with a `/`.

Lines that begin with a `;` are considered comments, and are ignored.  If a `;` appears anywhere else in a line, `;` and all text after it is ignored.

Variables can be created with the `/var` command; the first argument to `/var` is the name of the variable, and everything after the name is set as that variable's value.  Any created script variables are automatically interpolated into command input; put a '$' in front of the variable's name to substitute any references to that variable with that variable's value. All variable names are case-insensitive.

```
/var greeting Hello, world! ; Create a variable for our greeting
/var my_friend bob_jones    ; Create a variable for our private message target

/msg $my_friend $greeting   ; /msg bob_jones Hello, world!
```

Scripts can also execute the contents of a variable as a command.

```
/var connect_to_undernet /connect irc.undernet.org 6667 ; Set a variable's value to the command we want to execute
$connect_to_undernet                                    ; Execute the command
```

## Example Quirc Script

For the purpose of an example, let's assume you want to connect to your favorite channel on Undernet, `#quirc`. Your nick is registered with channel services; your username is "quirc", and your password is "changeme". You'll be auto-opped in `#quirc` as soon as you join the channel. You want to connect to IRC, log into channel services, join `#quirc`, and let everyone know you've arrived automatically.

```
; My #quirc Script

/print My #quirc Script Version 1.0

/connect irc.undernet.org 6667                          ; Connect to the server

/delay 20 /msg X@channels.undernet.org quirc changeme   ; Wait around for 20 seconds to make sure
                                                        ; we've connected, and then log into channel services

/delay 25 /join #quirc                                  ; Join #quirc a few seconds after we log in

/delay 30 /msg $channel Hello, everybody!               ; Send a message shortly after we join
```

## Quirc GUI

![Quirc GUI](https://github.com/danhetrick/quirc/blob/master/quirc_gui_guide.png?raw=true)
