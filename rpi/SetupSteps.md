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
    System -> Network at Boot = Do not wait
    System -> Splash Screen = Disable
    Interfaces -> Enable everything except: Serial Console and Remote GPIO
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

### 5. Minor Changes in .bashrc

The .bashrc file is normally executed on each startup -- and it configures your personal environment.  Make some
minor changes to aid in your development.  Do this by using the editor 'nano'.  For example, from the command line
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
also points you to info on how to set up mosquitto on a PC -- that might be helpful for debugging.  You are encouraged to follow the steps in the article  to learn more on how MQTT works.

### 11. Make the Raspberry Pi an "Access Point"

Now for the most complicated step -- set up the raspberry pi as an "Access Point".  This will allow the Driver Station on the PC to reliably communicate with your robot when normal WiFi networks are not available  -- like at the pool side.

Although complicated, this step is easy if you follow the instructions here: https://www.raspberrypi.org/documentation/configuration/wireless/access-point-routed.md

Below, are all the steps in condensed form, customized for our use.

	sudo apt install hostapd
	sudo systemctl unmask hostapd
	sudo systemctl enable hostapd
	sudo apt install dnsmasq
	sudo DEBIAN_FRONTEND=noninteractive apt install -y netfilter-persistent iptables-persistent
	sudo nano /etc/dhcpcd.conf
		=> Add these lines to the end of his file:
		interface wlan0
		static ip_addresss=10.0.5.1/24
		nohook wpa_supplicant
	sudo nano /etc/sysctl.d/routed-ap.conf 
		=> This will be a new file.  Put these lines in it:
		# https://www.raspberrypi.org/documentation/configuration/wireless/access-point-routed.md
		# Enable IPv4 routing
		net.ipv4.ip_forward=1
	sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
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

If you have trouble, after all this, you can edit the /etc/default/hostapd file and uncomment these lines:

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





