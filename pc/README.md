# Reference Code for WaterBot -- PC Side

The code in this folder and it's sub folders is intended to implement the drive station for a WaterBot on a PC, running Windows 10.

## Site Specific Configuration
The python reference code imports from a embeded lib directory.  You must add that lib 
directory to the python's search path by creating pth file in a site-packages folder.

For example, say that you have cloned this repository to C:\User\johndoe\Documents\RefWBot.  Then the embedded lib will be located here:

    C:\User\johndoe\Documents\RefWBot\pc\lib

You will need to create a file named "waterbot_pc.pth" file in the site-packages directory on your computer and put one line containing the directory in it.  That is, put the line above in the waterbot_pc.pth file.  The pth file sould be stored in the site-packages folder that can be found by starting a python REPL on a command line, importing sys, and typeing sys.path.  Pick a local site-packages directory to copy your pth file to.  For example, after creating the waterbot_pc.pth file with the proper path in it, on a commmand line do:

    copy waterbot_pc.pth C:\Users\johndoe\AppData\Local\Programs\Python\Python39\Lib\site-packages\waterbot_pc.pth

An example waterbot_pc.pth is included in this repository, but it probably won't work for you until you edit it and provide the proper directory.

## Development Environment

To properly set up a development enviroment, your PC should be equiped with the following:

1. Install vscode:   https://code.visualstudio.com/
2. Install Git:      https://desktop.github.com/
3. Install Python:   https://www.python.org/downloads/
4. Install MQTT:     https://mosquitto.org/download/

## Configure vscode
Vscode is a program that provides a Intergrated Develement Enviroment (IDE).  Since you will be doing most of your programming in python, it is best to configure vscode for python.  To do this, add the python extension to vscode.
Use google to figure out how.  One tip: make sure the enviroment for python that runs inside of vscode is the default for your Windows system.

It is also necessory to config vscode to work with github so that you can save your work on github. You need to read up on source control in vscode:
https://code.visualstudio.com/docs/editor/github

## GitHub
Make sure you have a GitHub account and can log into https://github.com/VCHSRobots.  You should have the ablity to change the RefWBot repository -- if not, talk to Mr. Brandon.  

## Learning Python
If you need to quickly learn Python, use https://www.w3schools.com/python/:  In about an hour you can read most of the topics (from Intro to Functions -- about 20 topics).  Once you have read these topics you should be able to understand and write typical python code.

## Configuring Python with MQTT
To use MQTT in Python -- you need to install the paho package.  Use a terminal window in vscode, and issue this command: "pip install paho-mqtt".
Read about installing and using MQTT with Python here: 
https://mntolia.com/mqtt-python-with-paho-mqtt-client/


