# ICE-V_Micropython
Micropython resources for use with the ICE-V Wireless board

## Abstract
This project is a work in progress to provide a set of hardware control functions
enabling Micropython to be used on the ICE-V Wireless board.

## Prerequisites
In order to use this you'll need to install Micropython on your ICE-V Wireless
board and configure it for a development environment.

### Micropython

Installation instructions for Micropython on the ESP32C3 are available at this
site:

https://micropython.org/download/esp32c3-usb/

Note that the USB port for your ICE-V Wireless board will likely not be the same
as that given in the instructions at that site so be sure to use the right port
name.

### WebREPL client
WebREPL is a networking protocol for Micropython that allows connection to the
REPL and file transfers via WiFi. Since the ESP32C3 used on the ICE-V Wireless
board doesn't have a USB device port capable of supporting MSD protocols it can't
emulate a FAT filesystem the way other Micropython systems can, so WebREPL provides
a way to transfer files to/from Micropython running on it. Client tools for
interacting with WebREPL can be found here:

https://github.com/micropython/webrepl

### Thonny

Thonny is a decent IDE that can interface with Micropython via WebREPL. Get it
here:

https://thonny.org/

## Setup
After installing Micropython on the ICE-V Wireless board it will need to be
set up to connect to your network and run WebREPL. This requires a bit of
manual configuration.

First, use a serial terminal application to connect to Micropython on the ICE-V
board. Try a bit of Python to make sure it's working correctly.

Next, enable WebREPL:
```
import webrepl_setup
```
Follow the prompts to (E)nable WebREPL, provide it with a password you can
remember easily and then allow it to reboot.

After that you'll need to connect to your network. Use these commands:
```
import network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('YOUR_SSID', 'YOUR_PASSWORD')
```

At this point your ICE-V Wireless board should be on the network. Use the
following command to determine its IP address:
```
wlan.ifconfig()
```
The first address in the resulting list is the IP address of your board.

Now start up the WebREPL server with the following commands:
```
import webrepl
webrepl.start()
```

## Running WebREPL in a browser
Now you should be able to connect with the WebREPL client in your browser. Open
the `webrepl.html` file from the webrepl github repo you cloned above in a
browser tab using the `file:\\\` URL and enter the IP address of your board
into the box in the upper left corner. Click the "Connect" button and enter
the password you created when you ran `webrepl_setup` above. This should
connect to your board.

## Setting up an automatic connection
In order for your ICE-V Wireless board to automatically connect to your network
every time it is powered up you will need to modify the boot script in the
root directory of your Micropython filesystem.

### Get the Boot script
Use the WebREPL browser client to do this via the "Get a File" box on the right
side of the screen. Enter thename `boot.py` in the text box and click the
"Get from Device" button.

### Modify the Boot script
Using a text editor, add the following code:
```
def do_connect():
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect('YOUR_SSID', 'YOUR_PASSWORD')
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())

# start networking
do_connect()
```
Make sure that this is added BEFORE the portion of the script that starts up
the WebREPL server.

### Send the Modified File
Copy the modified file back to your ICE-V Wireless board by clicking on the 
"Choose File" button in the "Send a File" box on the upper right of the screen.
Navigate to the location of your modified boot script, click the "Open" button and
then click the "Send to Device" button.

Now your ICE-V Wireless board should automatically connect to your WiFi network
and start a WebREPL server each time it powers up.

### Saving an FPGA Bitstream to the Micropython Filesystem
Using the "Send a File" feature of the WebREPL browser client, you may also
want to save a working FPGA bitstream to the filesystem. A good test bitstream
is the one that's included in the baseline repository:

https://github.com/ICE-V-Wireless/ICE-V-Wireless/blob/main/Firmware/spiffs/bitstream.bin

## Using Thonny
To allow Thonny to connect directly to WebREPL running on your ICE-V Wireless
board you will need to add its address to the Thonny options. Navigate to the
"Tools->Options->Interpreter" menu tab.

Under "Which Interpreter should Thonny use..." near the top of the page there
is an option box. Choose "Micropython (ESP32)". Further below is another option
box labled "Port or WebREPL" - choose "WebREPL" and enter the IP address and
password of your ICE-V Wireless board in the boxes below.

At this point Thonny should be connected to your ICE-V Wireless board and you
will be able to send Python scripts to it and use the REPL box below to run
them.

## Using the ICE-V Python code
Load the `fpga.py` script from this repo into Thonny and click F5 to send it to
your board. Using the bitstream file you sent to the board above, in the REPL
type the following:
```
f = FPGA()
f.setup()
f.FPGA_Config_File('bitstream.bin')
f.FPGA_CSR_Read(0)
```
This will load the bitstream and query the CSR at address 0. The result should
be 2953773056.

