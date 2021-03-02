# joystickwidget.py -- joystick widget to show joystick inputs
# EPIC Robotz, dlb, Mar 2021

import tkinter as tk

horz_px = 200
vert_px = 200
xorg = 100
yorg = 100
barlen2 = 75   # one side bar lenght in px
barwidth2 = 10  # one half of bar width in px
linewidth = 2

class JoystickWidget(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent, borderwidth=2, relief="groove")
        self.drawsurface = tk.Canvas(self, width=horz_px, height=vert_px, borderwidth=0,
            highlightthickness=0, background='white')
        self.drawsurface.pack(padx=10, pady=10)
        rawpoints = [(-barwidth2, barwidth2),
            (-barwidth2, barwidth2), (-barwidth2, barlen2), (barwidth2, barlen2),
            (barwidth2, barwidth2), (barlen2, barwidth2), (barlen2, -barwidth2),
            (barwidth2, -barwidth2), (barwidth2, -barlen2), (-barwidth2, -barlen2),
            (-barwidth2, -barwidth2), (-barlen2, -barwidth2), (-barlen2, barwidth2),
            (-barwidth2, barwidth2)]
        relpoints = [(x+xorg, y+yorg) for x,y in rawpoints]       
        self.drawsurface.create_polygon(relpoints, outline="blue", fill="lightgrey", width=linewidth)
        self.xdir = self.drawsurface.create_rectangle(xorg-linewidth, yorg+(barwidth2-linewidth),
            xorg+linewidth, yorg-(barwidth2-linewidth), fill="red", outline="red")
        self.ydir = self.drawsurface.create_rectangle(xorg-(barwidth2-linewidth), yorg-linewidth,
            xorg+(barwidth2-linewidth), yorg+linewidth, fill="red", outline="red")
        self.joyaxis = (0.0, 0.0, 0.0)
        self.joybtns = [False for x in range(12)]
        self.showaxes()
        self.showbtns()

    def setaxis(self, *args):
        ''' Sets the axis values for x, y, and z directions. 0-3 axes can be given.  Axis values range from -1.0 to 1.0 '''
        if len(args) >= 3:
            self.joyaxis = args[:3]
        elif len(args) == 2:
            x, y = args[:2]
            z = self.joyaxis[2]
            self.joyaxis = (x, y, z)
        elif len(args) == 1:
            x = args[0]
            y, z = self.joyaxis[1], self.joyaxis[2]
            self.joyaxis = (x, y, z)
        else:
            return
        self._fixaxis()
        self.showaxes()

    def _fixaxis(self):
        ''' clamps the axes values to -1.0 to 1.0. '''
        r = []
        for a in self.joyaxis:
            if a < -1.0: a = -1.0
            if a > 1.0: a = 1.0
            r.append(a)
        self.joyaxis = tuple(r)

    def showaxes(self):
        pass

    def showbtns(self):
        pass

