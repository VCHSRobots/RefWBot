# Raspberry Pi Setup and Configuration
## EPIC Robotz, dlb, Feb 2021

Follow these steps for a complete installation of the RPi software from scratch.

### 1. Make an Image of the OS.

 On a PC download the imager program from here:  https://www.raspberrypi.org/software .

Then, insert an SD card in the PC and run the imager program.  It will write the OS image on the SD Card.
If you are going to do this more than once, you might want to download the actual image first,
from here:  https://www.raspberrypi.org/software/operating-systems/
and then use the imager in custom mode.

### 2. Do Initial Powerup Configuration
Start up the Pi with a connected monitor, keyboard, and mouse.
Run through the automatic configuration questions, setting a password, setting up Wifi,
and so forth. I suggest that you choose "epic" as the password when it asks.  Reboot.

### 3. Do Overall Configuration
This can be done from the GUI, using: Preferences->Raspberry Pi Configuration.
These are the settings you want:
        
    System -> Boot=To Desktop,
    System -> Auto Login = to user 'pi'
	System -> Hostname = WaterBot  (or something you like)
    System -> Network at Boot = Do not wait
    System -> Splash Screen = Disable
    Interfaces -> Enable: Camera, SSH, VNC, I2C, Serial Port. Disable: SPI, Serial Console, 1-Wire, Remote GPIO.
    Localization  -> Do what you think best, but normally choose the correct timezone, country, and keyboard.
    Other Tabs -> No changes from default.

Then reboot again.

### 4. Work Remotely
In case we want to work remotely, so that you no longer need a monitor/keyboard/mouse plugged into your raspberry pi, do this step.

Open a command window on the RPi and type: "ifconfig".  This will give a report of your network settings.  Under WLAN0 you
should see an IP address similar to this: 192.168.1.35.  Remember this IP address, for the next steps. (Note: that if the
power is cycled on the pi, this address might change).

Use your PC, and start a command terminal.  

Issue the command: ssh pi@192.168.1.35   (substitute  the IP address that you found in the above step) and answer yes
if it warns you about authenticity.  Then give the password ("epic") when it asks 
and you should have a command line terminal to the Rpi.  At this point you can work on your PC and issue commands.

Or you can continue to work from the monitor/keyboard/mouse connected directly to the pi.  

Note that after you have finished step 12 below, you will no longer need the IP address you use here, since the Rpi's address
will always be 10.0.5.1 once you connect to it with WiFi.


### 5. Minor Changes in .bashrc

The .bashrc file is normally executed on each startup -- and it configures your personal environment.  Here, we make some
minor changes to aid in development.  Do this by using the editor 'nano'.  For example, from the command line
do:

	cd
	nano .bashrc
		=> use the nano editor to add the lines below and then save the file
	source .bashrc

To continue this example, in the .bashrc file, add these lines to the end of the file:
	
	alias python=python3
	alias pip=pip3
	alias cdw='cd /home/pi/RefWBot/rpi'
	export PATH="/home/pi/RefWBot/rpi/bin:$PATH"
	alias gobot='python /home/pi/RefWBot/rpi/runbot.py'


### 6. Get Up-To-Date Software
Make sure the software on your system is up-to-date.  Do this at the terminal by:

	sudo apt update
	sudo apt upgrade

### 7.  Git
Install Git (used to clone the software you will need). Do this at the terminal by:

	sudo apt install git
    
Git might already have been installed.  If so, this does no harm, and the system will tell you that.

### 8. Configure Git
You can configure git so that it works well with your username and email.  And even add SSH keys
to both the RPi and your github account so that you can move code back easily.  This is explained below.

HOWEVER, we have found that it is easier to do all development and interaction with git and github on 
the pc.  You edit your files on the pc, use git on your pc to store your code in github, and then copy
the entire repository from the pc to the RPi each time you want to run new code.  This is accomplished
with the Deploy.bat command on the pc.

If you still want to configure git, here's how:  First, configure git with your username and email so
that it doesn't always ask.  This assumes that you have a github account -- if not, go to github and create one.

	git config --global user.name "John Robot"
	git config --global user.email "johnrobot@vcschools.org"

As an option, you might consider configuring git for SSH.  This is necessary if you use two-level authentication
for github, as Mr. Brandon does. Even if your github account doesn't need two-level auth, this step might make
it easier to use github.

See: https://docs.github.com/en/github/authenticating-to-github/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent

Choose Linux in the tab.  Follow the instructions.

### 9. Copy (or clone) the Reference Code
As explained in step 8 above, you probably want to work on your pc and copy the code down to the RPi when you are 
ready to try it.  To prepare for that, do:

	cd
	mkdir RefWBot

Then, once you have set up your PC, the deploy.bat command will work.

However, you can use git to install the code too.  Installing from github for the first time is called "cloning".
First, make sure your current directory is in the right place, then issue the clone command, like so:
	
    cd
	git clone git@github.com:VCHSRobots/RefWBot.git

At this point, you should have a folder under your home directory, named "RefWBot" that contains the reference  code.

### 10. Install MQTT
The MQTT protocol is used to communicate between the Driver Station on the PC and the RPi.  We use an implementation of MQTT called mosquetto. A detailed account on how to do this is found here:
https://appcodelabs.com/introduction-to-iot-build-an-mqtt-server-using-raspberry-pi

The commands are:

	sudo apt install mosquitto mosquitto-clients
	sudo systemctl enable mosquitto

The web article  tells how to verify that mosquitto is working correctly.  You should try out those steps.  The article 
also points you to info on how to set up mosquitto on a PC -- that might be helpful for debugging.  You are encouraged to follow the steps in the article to learn more on how MQTT works.

If you want to check that mqtt is running property, use:

	sudo systemctl status mosquitto

This will give you a print out of the status.  In that you should see "active (running)" in green.

You will also need to have a python package, called paho-mqtt, installed in your python site-packages so that python can work with mqtt.  This is done by:

	pip install paho-mqtt



### 11. Make the Raspberry Pi an "Access Point"

Now for the most complicated step -- set up the raspberry pi as an "Access Point".  This will allow the Driver Station on the PC to reliably communicate with your robot when normal WiFi networks are not available  -- like at the pool side.

Although complicated, this step is easy if you follow the instructions here: https://www.raspberrypi.org/documentation/configuration/wireless/access-point-routed.md

Below, are all the commands in condensed form, customized for our use.  Be careful not to make any typos.

	sudo apt install hostapd
	sudo systemctl unmask hostapd
	sudo systemctl enable hostapd
	sudo apt install dnsmasq
	sudo DEBIAN_FRONTEND=noninteractive apt install -y netfilter-persistent iptables-persistent
	sudo nano /etc/dhcpcd.conf
		=> Add these lines to the end of his file:
		interface wlan0
		static ip_address=10.0.5.1/24
		nohook wpa_supplicant
	sudo nano /etc/sysctl.d/routed-ap.conf 
		=> This will be a new file.  Put these lines in it:
		# https://www.raspberrypi.org/documentation/configuration/wireless/access-point-routed.md
		# Enable IPv4 routing
		net.ipv4.ip_forward=1
	sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

	(Note: if the above line results in an error, try rebooting with 'sudo reboot now', and then 
	issuing it again.)

	sudo netfilter-persistent save
	sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
	sudo nano /etc/dnsmasq.conf
		=> This will be a new file.  Put these lines in it:
		interface=wlan0 # Listening interface
		dhcp-range=10.0.5.2,10.0.5.40,255.255.255.0,24h   # Pool of IP addresses served via DHCP
		domain=wlan     # Local wireless DNS domain
		address=/gw.wlan/10.0.5.1   # Alias for this router
	sudo rfkill unblock wlan
	sudo nano /etc/hostapd/hostapd.conf
		=> This will be a new file.  Put these lines in it:
		country_code=US		
		interface=wlan0
		ssid=RefBotA              <-- Put the name of your bot here
		hw_mode=g		  <-- You might consider changing this line and the next
		channel=7		  <-- based on your Drive Station PC.  Read up on this first!
		macaddr_acl=0
		auth_algs=1
		ignore_broadcast_ssid=0
		wpa=2
		wpa_passphrase=epic4fun   <-- Change this if you want security from other teams. Must >=8 chars.
		wpa_key_mgmt=WPA-PSK
		wpa_pairwise=TKIP
		rsn_pairwise=CCMP
	sudo systemctl reboot

Once all this is done, you should see your Raspberry Pi in your WiFi list on your pc.  Select it, and connect
to it from your pc.  Then open up a terminal (with the cmd program, or a erminal in Visual Code) on your pc,
and do:
	
	ssh pi@10.0.5.1

This should result in a question about connecting to a host for the first time. Answer "yes".  Then you will
need to provide the password for your raspberry pi which should be "epic" if you followed the recommendations
above.  After that the terminal should print something like "pi@waterbot:~ $".  This means you are connected
to the pi, and it is waiting for you to type a command.

If you have trouble, after all this, you can edit the /etc/default/hostapd file on the pi, and uncomment these lines:

	DAEMON_CONF="/etc/hostapd/hostapd.conf"
	DAEMON_OPTS="-dd -t -f /home/pi/hostapd.log"

Then you can view the log file for clues.  Also these following commands might be useful to gain other clues to whats wrong:

	systemclt status hostapd
	iw dev wlan0 info
	ifconfig

### 12. Setting up the Path for Python
The reference python program requires libraries to run.  Some of these libraries come from other programmers who have shared 
them on github and have provided them for general use.  Normally these libraries can be installed with the 'pip' command,
like so:

	pip install paho-mqtt

You will need paho-mqtt, so you should issue the above command on a terminal on the RPi. The pip command installs the library
in a place ("site-packages") where python can find it.

However, for the reference software, there are two custom librarys that must be installed by hand.  Actually, the libraries
are subject to change a lot, so we instead tell python where to find these custom librarys by installing a "pth" or path file
in the site-packages directory.  This is how that is done:  First run python in a terminal on the RPi.  In python, type the following lines:

		>>> import sys
		>>> sys.path

The sys.path command should cause python to print a list of directories.  One of these directries will have the name "site-packages"
as its final sub-directory.  Remember that one.  It should be something similar to: "/home/pi/.local/lib/python3.7/site-packages" --
that is the directory we want to put the pth file in.  If you are using the standard file layout, then you can do:

	cd /home/pi/RefWBot/rpi 
	cp waterbot.pth /home/pi/.local/lib/python3.7/site-packages/.

If you are using a non-standard setup, then you will need to edit waterbot.pth afterwards, and provide the proper directories for the libraries.

Under the standard setup, the two custom libraries that need to be accessed are:

	/home/pi/RefWBot/rpi/lib
	/home/pi/RefWBot/sharedlib

These are also the lines that should be in waterbot.pth that is stored in the site-packages directory.

### 13. Slowing Down the I2C Bus
The I2C bus that moves data between the RPi and the other hardware (the Arduino and the PCA9685 Module) needs to be slowed down for
reliable operation.  This requires editing the boot configuration file.  Do:

	sudo nano /boot/config.txt

In that file, search for the line that says: "dtparam=i2c_arm=on", and change it to the following (with NO spaces):

	dtparam=i2c_arm=on,i2c_arm_baudrate=40000

You must reboot the Rpi to make this take effect.

### 14. Setting up the bin Directory
The bin directory is located at /home/pi/RefWBot/rpi/bin.  It contains utilities that are useful in debugging hardware issues.
You should first use the Deploy command on the PC to copy all the raspberry Rpi software to the Rpi.  Then log into the pi
with a terminal.  Navigate to the bin directory with:

	cdw         (this should move you to the rpi subdirectory)
	cd bin		(after this you should be at /home/pi/RefWBot/rpi/bin)
	sudo apt install dos2unix
	dos2unix * 
	chmod +x *

These commands will convert all the py scrips so that they have the correct line endings for unix, and also have the correct 
prermissions to run on unix.  If you issue an "ll" command, they should all be green which means they have permission to
run.

### 15. Checking Things Out
Make sure that all the hardware is correctly connected and running with these commands on a Rpi Terminal:

	i2cdetect 1       

This command will warn you and ask if it should proceed.  Answer with y.  This will run a I2C diagnostic and print
out a address map.  The map should look like this:

			0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
		00:          -- -- -- -- -- 08 -- -- -- -- -- -- --
		10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
		20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
		30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
		40: -- -- -- -- -- -- -- -- -- -- -- -- 4c -- -- --
		50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
		60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
		70: -- -- -- -- -- -- -- --

The 08 is the arduino, and the 4c is the PCA9685 module.  If you have other hardware attached on the I2C bus, it should
show up.  If there is a 40 and not a 4C, then the PCA9685 module doesn't have the right address -- and it's address
pads needs to be soldered.  See the README in the top directory for instructions about that.

If the devices are not showing up, then the SCL and SDA wires are probably mixed up, or there is a problem with the 
level shifters or the cable between the Raspberry Pi and the IO board.

Next, run a diagnostic that tests the I2C bus reliability:

	cdw
	cd diagtest
	python i2ctst.py

The i2ctst.py program reads and writes to the arduino, and checks for errors.  It should be able to run for hours
without detecting an error.  It's output looks like:

	Loop Count: 50,  Bus Errors: 0,  Data Errors: 0
	Loop Count: 100,  Bus Errors: 0,  Data Errors: 0
	Loop Count: 150,  Bus Errors: 0,  Data Errors: 0
	Loop Count: 200,  Bus Errors: 0,  Data Errors: 0
	...

This will continue until you do control-C. If data errors are found, then something is wrong with the hardware or
the i2c baudrate -- see step 13.

Another useful program is regdump.  Issue that, and you should get an output similar to:

	Device Id = e
	Device Time = 1847310  (0e 30 1c 00)
	Batterys: Motors = 11.9, Logic = 12.1
	Analog (A1, A2, A3, A6, A7) =  0.000  0.008  0.024  0.067  0.067
	Digital Bits (D8-D3) = 80    F F F F F F
	Change Bits  (D8-D3) = 80
	PWM values (PWM9-11) = 0, 238, 0
	Spare regs =  23, 0, 0

Check the battery readings -- they should match your batteries, and the Device Id should be "e".  If you reissue
the regdump command, the Device Time should be inscreasing at a rate of 1000 per second.

You can also connect a servo to channel 15 of the PCA9685 module, and issues the following commands:

	initservos
	setservo 15 1000
	setservo 15 2000

These should cause the servo to move if the motor battery is turned on.

If all the above is successful, you can move forward with wiring you robot with confidence that the
control system is correctly set up.










