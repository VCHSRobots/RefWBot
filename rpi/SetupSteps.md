# Raspberry Pi Setup and Configuration
## EPIC Robotz, dlb, Feb 2021

Follow these steps for a complete installation of the RPi software from scratch.

### 1. Make an Image of the OS.

 On a PC download the imager program from here:  https://www.raspberrypi.org/software .

Then, insert an SD card in the PC and run the imager program.  It will write the OS image on the SD Card.  If your going to do this more than once, you might want to download the actual image first, from here:  https://www.raspberrypi.org/software/operating-systems/
and then use the imager in custom mode.

### 2. Do Inital Powerup Configuration
Start up the Pi with a connected monitor, keyboard, and mouse.
Run through the automatic configuration questions, setting a password, setting up Wifi, and so forth. I suggest that you choose "epic" as the password when it asks.  Reboot.

### 3. Do Overall Configuration
This can be done from the GUI, using: Preferences->Raspberry Pi Configuration.  These are the settings you want:
        
    System -> Boot=To Desktop,
    System -> Auto Login = to user 'pi'
    System -> Network at Boot = Do not wait
    System -> Splash Screen = Disable
    Interfaces -> Enable everything except: Serial Console and Remote GPIO
    Locaization -> Do what you think best, but normally choose the correct timezone, country, and keyboard.
    Other Tabs -> No changes from default.

Then reboot again.

### 4. Work Remotely
In case we want to work remotely, so that you no longer need a monitor/keyboard/mouse plugged into your raspberry pi, do this step.

Open a command window on the RPi and type: "ifconfig".  This will give a report of your network settings.  Under WLAN0 you should see an IP addres simpliar to this: 192.168.1.35.  Remember this IP address, for the next steps. (Note: that if the power is cycled on the pi, this address might change).

Use your PC, and start a command terminal.  

Issue the command: ssh pi@192.168.1.35   (substitude the IP addresss that you found in the above step) and answer yes if it warns you about authenticity.  Then give the password ("epic") when it asks 
and you should have a command line terminal to the Rpi.  At this point you can work on your PC and issue commands.

Or you can continue to work from the monitor/keyboard/mouse connected directly to the pi.  

### 5. Minor Changes in .bashrc

The .bashrc file is normally executed on each startup -- and it configures your personal environment.  Make a minor change to add an
alises for showing files in a folder.  For example:

	cd
	nano .bashrc
	=> use the nano editor to remove comments for the alias ll, then save the file
	source .bashrc


### 6. Get Up-To-Date Software
Make sure the software on you system is up-to-date.  Do this at the terminal by:

	sudo apt update
	sudo apt upgrade

### 7.  Git
Install Git (used to clone the software you will need). Do this at the terminal by:

	sudo apt install git
    
Git might already have been installed.  If so, this does no harm, and the system will tell you that.

### 8. Configure Git
Configure git with your username and email so that it doesn't always
ask.  This assumes that you have a github account -- if not, go to github and create one.

	git config --global user.name "John Robot"
	git config --global user.email "johnrobot@vcschools.org"

As an option, you might consider configuring git for SSH.  This is necessary if you use two-level authentication for github, as Mr. Brandon does. Even if your github account doesn't need two-level auth, this step might make it easier to use github.

See: https://docs.github.com/en/github/authenticating-to-github/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent

Choose Linux in the tab.  Follow the instructions.

### 9. Clone the Reference Code
Install the robot code for the first time.  This is called "cloning".  First, make sure your current directory
is in the right place, then issue the clone command, like so:
	
    cd
	git clone git@github.com:VCHSRobots/RefWBot.git

At this point, you should have a folder under your home directory, named "RefWBot" that contains the referece code.

### 10. Install MQTT
The MQTT protocol is used to communicate between the Driver Station on the PC and the RPi.  We use an impletation of MQTT called mosquetto. A detailed account on how to do this is found here:
https://appcodelabs.com/introduction-to-iot-build-an-mqtt-server-using-raspberry-pi

The commands are:

	sudo apt install mosquitto mosquitto-clients
	sudo systemctl enable mosquitto

The web artical tells how to verify that mosquitto is working correctly.  You should try out those steps.  The artical
also point you to info on how to set up mosquitto on a PC -- that might be helpful for debugging.  You are encouraged to follow the steps in the artical to learn more on how MQTT works.

### 11. Make the Raspberry Pi an "Access Point"

Now for the most complicated step -- set up the raspberry pi as an "Access Point".  This will allow the Driver Station on the PC to reliable communicate with your robot when normal WiFi networks are not avaliable -- like at pool side.

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



1. Make sure you install the CH340 Driver on your PC from here: 
	https://learn.sparkfun.com/tutorials/how-to-install-ch340-drivers/all
The window's version is a long way down the page.