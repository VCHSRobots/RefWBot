# Arduino Setup
__Epic Robotz, dlb, Feb 2021__


### 1. Get the Windows Driver for the Nano

 Make sure you install the CH340 Driver on your PC.  One place to get it is from here: 
	https://learn.sparkfun.com/tutorials/how-to-install-ch340-drivers/all

The link to the window's version is a long way down the page.

### 2. Get the Arduino IDE

The arduino IDE can be downloaded here: https://www.arduino.cc/en/software

### 3. Configure the IDE
First, plug in your Nano with a USB cord.  The Nano should light up, and the PC should make USB connecting sounds.  If the PC doesn't acknowledge some sort of connection it is probably because you are using a "charge only" USB cable. Get another cable and try again.

Once the Nano is actually connected to the PC, do the following in the IDE:

    1. Set Tools->Board->Arduino AVR Boards->Arduino Nano
    2. Set Tools->Processor->"ATmega32BP (Old Bootloader)"
    3. Set Tools->Port 
        (To the COM port that is shown... usually only one, 
        and it's the one you have plugged the Nano into.)

### 4. Test the Connection
In the IDE, do Tools->Get Board Info.  If all goes well, you should see a dialog box with info about the Nano, such as BN, VID, PID, and SN.

### 5. Load the Software and Upload it to the Arduino.
Using the IDE, open "RobotRun" from the reference repository.  That is located at ...\RefWBot\arduino\RobotRun.  Then click the Upload arrow in the IDE.  

### 6. Verify All is Well
If all goes well, you shouldn't see any errors, and the software on the RPi should be able to communicate with the Arduino.  For example 
on the raspberry, execute the following commands:

    cd RefWBot/rpi
    bin/regdump

That should print out the status of the raspberry pi.

### 7. Enable Verbose Output for Errors
If you do have problems, it is helpful to have the IDE show more information as it works.  Go to File->Preferences and set "show verbose output on" and check the boxes for compliation and upload.




