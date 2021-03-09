## Raspberry Pi Code for Water Bot Control System

This folder and it's subfolders contain code that runs on the
Raspberry Pi for the Water Bot Control System. 

### Important Notes for Installing This Software

In general, this software expects to be installed in the /home/pi directory on your RPi,
and run under version 3 of python.  Starting in the directory /home/pi, you can use

    git clone git@github.com:VCHSRobots/RefWBot.git

to install the software.  The code that will run during the competition will be 

    /home/pi/RefWBot/rpi/runbot.py

For this software and its various utilities to run correctly, you should add /home/pi/RefWBot/rpi/lib to the search path for python.
This can be done by adding the waterbot.pth file to the site-packages for your version of python.  Do do this, issue a command that is 
similar to:

    cp ~/RefWBot/rpi/waterbot.pth ~/.local/lib/python3.7/site-packages/.

This will copy additional path instructions for python to use each time python runs for the
'pi' user.  Note, you must replace '3.7' for whatever version of python you are using.

### General Raspberry Pi Configuration

This section explains the general configuration for the Raspberry PI.  See "SetupSteps.md" in this directory for a detailed,
step-by-step description to configure a fresh Raspberry PI. 

There are many steps to setting up your RPi, as follows:

1. Install Git -- so that you can clone and develop the code that will run on the RPi.
   Note from the future: Although git is useful, we have found it is faster to develop on a pc, use git there,
   and just copy all the files down to the pi.  Therefore, having Git on the pi is not as useful.

2. Install and configure MQTT -- This is required for interfacing with the Drive Station (via WiFi) that runs on the PC.

3. Configure your RPi to be a WiFi access point.  This will allow you to connect with your Drive Station at the pool
   without a router.  And you can hard-code it's IP address so that you won't need to change your code right before an event.

4. Enable the I2C interface so that your RPi can connect to the hardware in your robot -- right now that is the Arduino and the PCA9685 module.

5. Set up a code directory to hold the robot program that runs on the RPi -- this will be a clone of your repository on github.

6. Install and enable VNC -- this will allow you to view the RPi's screen on your PC -- it could be a way that you could see video from the pi at your Drive Station.  

Useful links for understanding and completing the above steps:

- Installing git: 
    https://linuxize.com/post/how-to-install-git-on-raspberry-pi/ 
    (Don't do "build from the source" in this article.)

- Installing MQTT (mosquitto): https://appcodelabs.com/introduction-to-iot-build-an-mqtt-server-using-raspberry-pi

- WiFi Access point: https://www.raspberrypi.org/documentation/configuration/wireless/access-point-routed.md

- I2C: 
https://www.raspberrypi-spy.co.uk/2018/02/change-raspberry-pi-i2c-bus-speed/

- VNC: 
https://www.raspberrypi.org/documentation/remote-access/vnc/

### Notes
1. When configuring the Access Point software (a long and complicated step), you should use 10.0.5.1 for the IP address of your RPi.  This is hard coded into the reference software, and you won't need to change it as you customize the reference design.  Your network will be on the 10.0.5.x addresses. If you do it this way, your WiFi network will not conflict with other teams since they will be connecting to their own RPi's network.  Even though both networks are on the same 10.0.5.x addresses, they will be on a different WiFi channel and ssid.
2. You, however, must choose a unique name for your ssid on your RPi's WiFi.  This is done when you edit the /etc/hostapd/hostapd.conf file.  In addition, you must be careful to set up the IP addresses to the 10.0.5.x addresses, instead of the 192.168.4.x addresses described in the article. (That is, just change 192.168.4 to 10.0.5 at each occurance.)
3. The reference RPi's ssid is "RefWBot".  The WiFi password for the reference RPi is the normal one used by EPIC robotz. 
4. When enabling I2C, you probably WILL need to change the baud rate -- it seems to work reliably at 10KHz instead of the default of 100KHz.
5. When installing MQTT, its probably best to use the RPi as the broker.  That is because it's IP address will be fixed to 10.0.5.1 if you follow the recommendation in note 1.
6. The PCA9685 Module requires an address.  For the reference design it is set to 0x4C. You must set that address on the module itself by using a soldering iron to "jump" the correct Address bits (A5, A4, A3, A2, A1).  To get the 0x4C address, you must jump A3 and A4.  A3 and A4 provide the 'C' in the 0x4C.  The 4 in '0x4C' is automatically enabled by the chip (which means the default address of the chip is 0x40). Look carefully at a completed example to see how this is done.

### Schematic of Bot's Control System
![schematic](RPiHardware.PNG)
