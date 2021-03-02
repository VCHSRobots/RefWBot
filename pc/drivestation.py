# drivestation.py -- Drive Station Program for Reference Water Bot
# Epic Robotz, dlb, Mar 2021

import tkinter as tk
import tkinter.font as tkFont
import gameclockwidget
import joystickwidget

title = "EPIC ROBOTZ"
teamname = "Reference Bot"

class DriveStation(tk.Frame):

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self._titlefont = tkFont.Font(family="Copperplate Gothic Bold", size=28)
        self._namefont = tkFont.Font(family="Copperplate Gothic Light", size=22)
        self._titlelabel = tk.Label(self, text=title, anchor="center", font=self._titlefont)
        self._namelabel = tk.Label(self, text=teamname, anchor="center", font=self._namefont)
        self._gameclock = gameclockwidget.GameClockWidget(self)
        self._joystick = joystickwidget.JoystickWidget(self)

        self._titlelabel.pack(side="top", fill="x", padx=4, pady=4)
        self._namelabel.pack(side="top", fill="x", padx=4, pady=4)
        self._gameclock.pack(side="top", fill="x", padx=4, pady=4)
        self._joystick.pack(side="top", fill="x", padx=4, pady=4)



if __name__ == "__main__":
    root = tk.Tk()
    root.title("Driver Station for Water Bot")
    root.geometry('300x900')
    x1 = DriveStation(root)
    x1.place(x=0, y=0, relwidth=1, relheight=1)
    root.mainloop()
