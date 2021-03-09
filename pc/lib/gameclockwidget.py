# gameclockwidget.py -- code for the game clock widget
# EPIC Robotz, dlb, Mar 2021

import tkinter as tk
import tkinter.font as tkFont
import dscolors  
import time

GAMEMODE_Ready = 0
GAMEMODE_Auto = 1
GAMEMODE_Teleop = 2
GAMEMODE_Stopped = 3

bot_cmd = {GAMEMODE_Auto: "AUTO", GAMEMODE_Teleop: "TELEOP", GAMEMODE_Ready: "STOP", GAMEMODE_Stopped: "STOP"}

game_telesecs = 240
game_autosecs = 30
game_warnsecs = 15

desiredsize = (250, 150)  # desired size of widget for placing.

class GameClockWidget(tk.Frame):

    def __init__(self, parent):
        tk.Frame.__init__(self, parent, borderwidth=2, relief="groove", background=dscolors.widget_bg)
        self._bigfont = tkFont.Font(family="Lucida Grande", size=40)
        self._btnfont = tkFont.Font(family="Lucida Grande", size=16)
        self._modefont = tkFont.Font(family="Lucida Grande", size=16, weight="bold")
        self._modelabel = tk.Label(self, text="Standby", anchor="center", font=self._modefont)
        self._clocklabel = tk.Label(self, text="4:00", anchor="center", font=self._bigfont)
        self._mainbutton = tk.Button(self, text="Start Match", font=self._btnfont, 
            width=10, bg=dscolors.button_bg, command=self._switch_mode)
        self._modelabel.pack(side="top", fill="x", padx=10, pady=0)
        self._clocklabel.pack(side="top", fill="x", padx=10, pady=0)
        self._mainbutton.pack(side="top", fill="x", padx=10)
        self._current_modenum = 0
        self._clockrunning = False
        self._clockvalue = game_telesecs + game_autosecs  # Clock value at clock0
        self._clock0 = time.monotonic()  # Wall clock time at start
        self._clockfinal = self._clockvalue  # Time remaining when clock is stopped.
        self._clockcurrentvalue = self._clockvalue  # For external querys to make sure we are passing value shown
        self._lastclock = (-1, -1, "black")
        self._showclock(self._clockvalue)
        self.after(50, self._updater)

    def get_size(self):
        ''' Returns the desired size for this widget. '''
        return desiredsize

    def _updater(self):
        ''' Timer update of clock and modes. '''
        self.after(50, self._updater)
        if not self._clockrunning:
            self._showclock(self._clockfinal)
            return
        secs_used = int(time.monotonic() - self._clock0)
        secs_to_go = self._clockvalue - secs_used
        if self._current_modenum == GAMEMODE_Auto:
            if secs_used > game_autosecs:
                self.setmode(GAMEMODE_Teleop)
                return
        if self._current_modenum == GAMEMODE_Teleop:
            if secs_to_go <= 0:
                self._clockfinal = 0
                self.setmode(GAMEMODE_Stopped)
                self._showclock(self._clockfinal)
                return
        self._showclock(secs_to_go)

    def _showclock(self, secs_to_go): 
        ''' Display current clock value on screen. '''
        if secs_to_go <= game_warnsecs:
            color = "red"
        else:
            color = "black"
        mins = int(secs_to_go / 60)
        secs = int(secs_to_go) - int(60 * mins)
        if self._lastclock == (mins, secs, color): return
        sval = "%d:%02d" % (mins, secs)
        self._clocklabel.configure(text=sval, fg=color)
        self._lastclock = (mins, secs, color)
        self._clockcurrentvalue = secs_to_go


    def _switch_mode(self):
        ''' Process manual mode switch. '''
        self._current_modenum += 1
        if self._current_modenum >= 4:
            self._current_modenum = 0
        self.setmode(self._current_modenum)

    def _showmode(self):
        ''' Display current mode on screen. '''
        if self._current_modenum == GAMEMODE_Ready:
            self._modelabel.configure(text="Standby", fg="green")
            self._mainbutton.configure(text="Start Match")
        elif self._current_modenum == GAMEMODE_Auto:
            self._modelabel.configure(text="Auto", fg="green")
            self._mainbutton.configure(text="Go Teleop")
        elif self._current_modenum == GAMEMODE_Teleop:
            self._modelabel.configure(text="TeleOp", fg="blue")
            self._mainbutton.configure(text="Stop")
        else:  #  GAMEMODE_Stopped
            self._modelabel.configure(text="Stopped", fg="red")
            self._mainbutton.configure(text="Reset")

    def setmode(self, modenum):
        ''' Sets up a new mode given by modenum which is
            one of the GAMEMODE_xxxx constants.'''
        self._current_modenum = modenum
        if self._current_modenum == GAMEMODE_Ready:
            self._clockvalue = game_telesecs + game_autosecs
            self._clockfinal = self._clockvalue
            self._clockrunning = False
            self._showclock(self._clockvalue)
        elif self._current_modenum == GAMEMODE_Auto:
            self._clockvalue = game_telesecs + game_autosecs
            self._clockrunning = True
            self._clock0 = time.monotonic()
            self._showclock(self._clockvalue)
        elif self._current_modenum == GAMEMODE_Teleop:
            self._clockvalue = game_telesecs
            self._clockrunning = True
            self._clock0 = time.monotonic()
            self._showclock(self._clockvalue)
        else:  #  GAMEMODE_Stopped
            self._clockrunning = False
            secs_used = int(time.monotonic() - self._clock0)
            self._clockfinal = self._clockvalue - secs_used
            self._showclock(self._clockfinal)
        self._showmode()

    def clock_value(self):
        ''' Returns the game clock's value in seconds to go. '''
        return self._clockcurrentvalue

    def get_mode(self):
        ''' Returns the current mode as one of the GAMEMODE_xxx integer constants.'''
        return self._current_modenum

    def get_botcmd(self):
        ''' Returns a (cmd, time_to_go) tuple suitable for commanding the robot. 
        The cmd will be one of "STOP", "TELEOP", "AUTO", and time_to_go will be the
        number of seconds remaining in that mode, or 0 for STOP. '''
        mode = bot_cmd[self._current_modenum]
        if self._current_modenum == GAMEMODE_Ready or self._current_modenum == GAMEMODE_Stopped:
            return (mode, 0)
        secs_used = time.monotonic() - self._clock0  # Work in floating point, unlike the display clock
        secs_to_go = self._clockvalue - secs_used
        if self._current_modenum == GAMEMODE_Auto:
            n = game_autosecs - secs_used
            if n < 0: n = 0
            return (mode, n)
        else:
            if secs_to_go < 0: secs_to_go = 0
            return(mode, secs_to_go)   


