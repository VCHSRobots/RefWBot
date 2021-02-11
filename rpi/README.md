## Raspberry Pi Code for Water Bot Control System

This folder and it's subfolders contain code that runs on the
Raspberry Pi for the Water Bot Control System. 

### Setting up the Raspberry Pi

There are many steps to setting up your RPi.  
1. Install Git -- so that you can clone and develop the code that will run on the RPi.
2. Install and configure MQTT -- This is required for interfacing with the Drive Station (via WiFi) that runs on the PC.
3. Configure your RPi to be a WiFi access point.  This will allow you to connect with your Drive Station at the pool without a router.  And you can hard-code it's IP address so that you won't need to change your code right before an event.
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
2. You, however must choose a unique name for your ssid on your RPi's WiFi.  This is done when you edit the /etc/hostapd/hostapd.conf file.  In addition, you must be careful to set up the IP addresses to the 10.0.5.x addresses, instead of the 192.168.4.x addresses described in the artical. (That is, just change 192.168.4 to 10.0.5 at each occurance.)
3. The reference RPi's ssid is "RefWBot".  The WiFi password for the reference RPi is the normal one used by EPIC robotz. 
4. When enabling I2C, you probably don't need to change the baudrate -- keep it at it's default of 100,000.
5. When installing MQTT, its probably best to use the RPi as the broker.  That is because it's IP address will be fixed to 10.0.5.1 if you follow the recommendation in note 1.

