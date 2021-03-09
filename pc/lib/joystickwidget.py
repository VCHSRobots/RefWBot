# joystickwidget.py -- joystick widget to show joystick inputs
# EPIC Robotz, dlb, Mar 2021

import tkinter as tk
import tkinter.font as tkFont
import math
import dscolors

# Constants to control the layout of the diagram:
desiredsize = (250, 200) # desired size of widget for placing
horz_px = 210 # horzontal size of the the widget in pixels
vert_px = 210 # vertial size of the widget in pixels
blockout = (0, 0, 200, 200) # block out rect for invalid flag
xorg = 100 # x orgin of the complete diagram. which is center of main cross bars.
yorg = 88 # y orgin of the complete diagram, which is center of main cross bars.
xytwist = (-80, 30, 50) # loc of arc center and size for twist diagram
zbar = (50, 30, 50, 10) # loc, len, width of z slider diagram
textloc = (0, 90) # center loc of the status text
barlen2 = 75   # one side bar lenght in px
barwidth2 = 10  # one half of bar width in px
linewidth = 2   # linewidth on edges of bars and buttons
btnsz = 8  # size of the buttons in px  
# locations of buttons relative to orgin
btnrectslocs=((-4, -88), (-25, -75), (16, -65), (26, -65), (16, -75), (26, -75), 
              (-75, -75), (-65, -75),(-75,-65), (-65, -65), (-75,-55), (-65, -55))

class JoystickWidget(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent, borderwidth=2, relief
        ="groove", bg=dscolors.widget_bg)
        self._canvas = tk.Canvas(self, width=horz_px, height=vert_px, borderwidth=0,
            highlightthickness=0, background=dscolors.widget_bg)
        self._canvas.pack(padx=4, pady=4)
        self._background = self._canvas.create_rectangle(*blockout, fill="", outline="")
        rawpoints = [(-barwidth2, barwidth2),
            (-barwidth2, barwidth2), (-barwidth2, barlen2), (barwidth2, barlen2),
            (barwidth2, barwidth2), (barlen2, barwidth2), (barlen2, -barwidth2),
            (barwidth2, -barwidth2), (barwidth2, -barlen2), (-barwidth2, -barlen2),
            (-barwidth2, -barwidth2), (-barlen2, -barwidth2), (-barlen2, barwidth2),
            (-barwidth2, barwidth2)]
        relpoints = [(x+xorg, y+yorg) for x,y in rawpoints]       
        self._canvas.create_polygon(relpoints, outline="blue", fill=dscolors.indicator_bg, width=linewidth)
        self._xdir = self._canvas.create_rectangle(xorg-linewidth, yorg+(barwidth2-linewidth),
            xorg+linewidth, yorg-(barwidth2-linewidth), fill=dscolors.indicator_fg, outline=dscolors.indicator_fg)
        self._ydir = self._canvas.create_rectangle(xorg-(barwidth2-linewidth), yorg-linewidth,
            xorg+(barwidth2-linewidth), yorg+linewidth, fill=dscolors.indicator_fg, outline=dscolors.indicator_fg)
        self._dot = self._canvas.create_oval(xorg-(barwidth2-linewidth), yorg-(barwidth2-linewidth),
            xorg+(barwidth2-linewidth), yorg+(barwidth2-linewidth), fill=dscolors.indicator_fg, outline=dscolors.indicator_fg)
        self._btnrecs = []
        for x, y in btnrectslocs: 
            x0, y0, x1, y1 = x+xorg, y+yorg, x+xorg+btnsz, y+yorg+btnsz
            b = self._canvas.create_rectangle(x0, y0, x1, y1,
                outline="black", fill=dscolors.indicator_bg, width=1)
            self._btnrecs.append(b)
        xz, yz, sz = xytwist
        x0, y0, x1, y1 = xorg + xz, yorg + yz, xorg + xz + sz, yorg + yz + sz
        self._zaxis1 = self._canvas.create_arc(x0, y0, x1, y1, start=20, extent=140,
            style=tk.ARC, width=14, outline="blue")
        self._zaxis2 = self._canvas.create_arc(x0, y0, x1, y1, start=20, extent=140,
            style=tk.ARC, width=10, outline=dscolors.indicator_bg)
        self._zaxis3 = self._canvas.create_arc(x0, y0, x1, y1, start=88, extent=2,
            style=tk.ARC, width=10, outline=dscolors.indicator_fg)
        xc, yc = xorg + xz + sz/2, yorg + yz + sz/2
        r1, r2 = sz/2 - 6, sz/2 + 6
        x0, y0 = int(xc - r1*math.sin(20)), int(yc - r1*math.cos(20))
        x1, y1 = int(xc - r2*math.sin(20)), int(yc - r2*math.cos(20))
        self._canvas.create_line(x0, y0, x1, y1, fill="blue", width=2)
        x0, y0 = int(xc + r1*math.sin(20)), int(yc - r1*math.cos(20))
        x1, y1 = int(xc + r2*math.sin(20)), int(yc - r2*math.cos(20))
        self._canvas.create_line(x0, y0, x1, y1, fill="blue", width=2)
        x, y, h, w = zbar
        x0, y0, x1, y1 = xorg + x, yorg + y, xorg + x + w, yorg + y + h
        self._zbar = self._canvas.create_rectangle(x0, y0, x1, y1, outline="blue",
                            fill=dscolors.indicator_bg, width=linewidth)
        self._zdir = self._canvas.create_rectangle(x0+linewidth, y0+linewidth, 
                    x1-linewidth, y1-linewidth, fill=dscolors.indicator_fg, outline=dscolors.indicator_fg)
        self._statusfont = self._bigfont = tkFont.Font(family="Lucida Grande", size=12)
        x, y = textloc
        self._status = self._canvas.create_text(x + xorg, y + yorg, text="Joystick",
                        state=tk.DISABLED, fill="black", anchor=tk.CENTER, font=self._statusfont)
        self._joyaxis = (0.0, 0.0, 0.0)
        self._joyruv = (0.0, 0.0, 0.0)
        self._joybtns = tuple([False for x in range(12)])
        self._lastaxis = None
        self._lastruv = None
        self._lastbtns = None
        self._lastmode = ''

        self._showaxes()
        self._showbtns()
        self._showruv()
  
    def get_size(self):
        ''' Returns the desired size for this widget. '''
        return desiredsize

    def set_mode(self, mode):
        ''' Sets the mode of the joystick.  Can be 'active' or 'invalid'.
        If 'active' the joystick works as normal.  If 'invalid' the 
        background is turned to yellow, and the words "Joystick Not Found"
        are shown at the bottom.  However, the diagrams continue to work
        as normal.'''
        if mode == self._lastmode: return
        self._lastmode = mode
        if mode == 'active':
            self._canvas.itemconfig(self._background, fill=dscolors.widget_bg, 
                    outline=dscolors.widget_bg)
            self.set_statustext(text="Joystick", color="black")
        if mode == 'invalid':
            self._canvas.itemconfig(self._background, fill=dscolors.indicator_invalid_bg, 
                    outline=dscolors.indicator_invalid_bg)
            self.set_statustext(text="Joystick Not Found", color="red")

    def set_axis(self, *args):
        ''' Sets the axis values for x, y, z directions. 0-3 values can be given.
        Axis values range from -1.0 to 1.0 '''
        if len(args) >= 3:
            self._joyaxis = args[:3]
        elif len(args) == 2:
            x, y = args
            z = self._joyaxis[2]
            self._joyaxis = (x, y, z)
        elif len(args) == 1:
            x = args[0]
            y, z = self._joyaxis[1], self._joyaxis[2]
            self._joyaxis = (x, y, z)
        else:
            return
        self._fixaxis()
        self._showaxes()

    def set_ruv(self, *args):
        ''' Set the RUV (orientation axis) for r, u, v angles.
        0-3 arguments can be given. Values should be between -1.0 and 1.0. '''
        if len(args) >= 3:
            self._joyruv = args[:3]
        elif len(args) == 2:
            x, y = args
            z = self._joyruv[2]
            self._joyruv = (x, y, z)
        elif len(args) == 1:
            x = args[0]
            y, z = self._joyruv[1], self._joyruv[2]
            self._joyruv = (x, y, z)
        else:
            return
        self._fixruv()
        self._showruv()

    def set_buttons(self, *buttons):
        ''' Sets the button states on the joystick display.
        0-12 booleans can be provided.'''
        if len(buttons) == 0:
            return
        elif len(buttons) >= 12:
            self._joybtns = tuple(buttons[:12])
        else:
            bnew = list(self._joybtns[:])
            i = 0
            for x in buttons:
                bnew[i] = x
                i += 1
            self._joybtns = tuple(bnew)
        self._showbtns()

    def set_statustext(self, text, color="black"):
        ''' Sets the status text under the diagram on the joystick. Note that
        this is the same status text used by the mode feature. '''
        self._canvas.itemconfig(self._status, text=text, fill=color)

    def _fixaxis(self):
        ''' clamps the axes values to -1.0 to 1.0. '''
        r = []
        for a in self._joyaxis:
            if a < -1.0: a = -1.0
            if a > 1.0: a = 1.0
            r.append(a)
        self._joyaxis = tuple(r)

    def _fixruv(self):
        ''' clamps the ruv values to -1.0 to 1.0. '''
        r = []
        for a in self._joyruv:
            if a < -1.0: a = -1.0
            if a > 1.0: a = 1.0
            r.append(a)
        self._joyruv = tuple(r)

    def _showaxes(self):
        ''' draws the position of the joystick on the diagram '''
        if self._joyaxis == self._lastaxis: return
        self._lastaxis = self._joyaxis
        x, y, z = self._joyaxis
        ix, iy = xorg - int(x * (barlen2-linewidth)), yorg - int(y * (barlen2-linewidth))
        x0, y0, x1, y1 = xorg, yorg + barwidth2 - linewidth, ix, yorg - barwidth2
        self._canvas.coords(self._xdir, x0, y0, x1, y1)
        x0, y0, x1, y1 = xorg + barwidth2 - linewidth, yorg, xorg - barwidth2, iy
        self._canvas.coords(self._ydir, x0, y0, x1, y1)
        xx, yy, h, w = zbar
        iz = int(z * h)
        if iz < 1: iz = 1
        if iz > h-linewidth: iz = h-linewidth
        x0, y0 = xorg + xx + linewidth - 1, yorg + yy - linewidth + h
        x1, y1 = xorg + xx + w - linewidth, yorg + yy - linewidth + h - iz  
        self._canvas.coords(self._zdir, x0, y0, x1, y1)

    def _showruv(self):
        ''' draw the angle of the twist on the diagram '''
        if self._joyruv == self._lastruv: return
        self._lastruv = self._joyruv
        val = self._joyruv[0]
        angle = int(val * 60.0)
        if angle > -3 and angle < 3:
            self._canvas.itemconfig(self._zaxis3, start=88, extent=2)
        else:
            self._canvas.itemconfig(self._zaxis3, start=90, extent=-angle)

    def _showbtns(self):
        ''' draws the conditions of the buttons on the diagram '''
        if self._joybtns == self._lastbtns: return
        self._lastbtns = self._joybtns
        icnt = 0
        for r in self._btnrecs:
            if self._joybtns[icnt]:
                self._canvas.itemconfig(r, fill=dscolors.indicator_fg)
            else:
                self._canvas.itemconfig(r, fill=dscolors.indicator_bg)
            icnt += 1

