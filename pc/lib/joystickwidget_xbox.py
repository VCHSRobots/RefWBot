# joystickwidget_xbox.py -- joystick widget to show joystick inputs for XBox gamepad
# EPIC Robotz, dlb, Mar 2021
# Rewriten from joystickwidget_logitech.py by Holiday P, March 2021

import tkinter as tk
import tkinter.font as tkFont
import math
import dscolors

# Constants to control the layout of the diagram:
desiredsize = (250, 200) # desired size of widget for placing
horz_px = 210 # horzontal size of the the widget in pixels
vert_px = 210 # vertial size of the widget in pixels
blockout = (0, 0, 200, 180) # block out rect for invalid flag
xorg = 100 # x orgin of the complete diagram. which is center of main cross bars.
yorg = 100 # y orgin of the complete diagram, which is center of main cross bars.
a1xorg = 50 # x origin of the right cross bars
a1yorg = 70 # y origin of the right cross bars
a2xorg = 150 # x origin of the left cross bars
a2yorg = 100 # y origin of the right cross bars
zbar1 = (-80, 5, 50, 10) # loc, len, width of the first z slider diagram
zbar2 = (80, 20, 50, 10) # loc, len, width of the second z slider diagram
textloc = (0, 73) # center loc of the status text
hatloc = (-30, 30) # center loc of the hats indicator
barlen2 = 40   # one side bar lenght in px
barwidth2 = 8  # one half of bar width in px
linewidth = 2   # linewidth on edges of bars and buttons
btnsz = 8  # size of the buttons in px
hatsz = 8
# locations of buttons relative to orgin
btnrectslocs=((75, -55), (83, -63), (67, -63), (75, -71), (-60, -95), (60, -95), 
              (-35, -80), (35, -80), (-39, -50), (62, -20),  (0, -95), (0, -80))

class JoystickWidget(tk.Frame):
    def __init__(self, parent):
        #Create main tk frame
        tk.Frame.__init__(self, parent, borderwidth=2, relief="groove", bg=dscolors.widget_bg)
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
        #Draw the pirst cross display
        relpoints = [(x+a1xorg, y+a1yorg) for x,y in rawpoints]       
        self._canvas.create_polygon(relpoints, outline="blue", fill=dscolors.indicator_bg, width=linewidth)
        self._xdir1 = self._canvas.create_rectangle(a1xorg-linewidth, a1yorg+(barwidth2-linewidth),
            a1xorg+linewidth, yorg-(barwidth2-linewidth), fill=dscolors.indicator_fg, outline=dscolors.indicator_fg)
        self._ydir1 = self._canvas.create_rectangle(a1xorg-(barwidth2-linewidth), a1yorg-linewidth,
            a1xorg+(barwidth2-linewidth), a1yorg+linewidth, fill=dscolors.indicator_fg, outline=dscolors.indicator_fg)
        self._dot1 = self._canvas.create_oval(a1xorg-(barwidth2-linewidth), a1yorg-(barwidth2-linewidth),
            a1xorg+(barwidth2-linewidth), a1yorg+(barwidth2-linewidth), fill=dscolors.indicator_fg, outline=dscolors.indicator_fg)
        #Draw the second cross display
        relpoints = [(x+a2xorg, y+a2yorg) for x,y in rawpoints]       
        self._canvas.create_polygon(relpoints, outline="blue", fill=dscolors.indicator_bg, width=linewidth)
        self._xdir2 = self._canvas.create_rectangle(a2xorg-linewidth, a2yorg+(barwidth2-linewidth),
            a2xorg+linewidth, a2yorg-(barwidth2-linewidth), fill=dscolors.indicator_fg, outline=dscolors.indicator_fg)
        self._ydir2 = self._canvas.create_rectangle(a2xorg-(barwidth2-linewidth), a2yorg-linewidth,
            a2xorg+(barwidth2-linewidth), a2yorg+linewidth, fill=dscolors.indicator_fg, outline=dscolors.indicator_fg)
        self._dot2 = self._canvas.create_oval(a2xorg-(barwidth2-linewidth), a2yorg-(barwidth2-linewidth),
            a2xorg+(barwidth2-linewidth), a2yorg+(barwidth2-linewidth), fill=dscolors.indicator_fg, outline=dscolors.indicator_fg)
        #Draw the buttons
        self._btnrecs = []
        for x, y in btnrectslocs: 
            x0, y0, x1, y1 = x+xorg, y+yorg, x+xorg+btnsz, y+yorg+btnsz
            b = self._canvas.create_rectangle(x0, y0, x1, y1,
                outline="black", fill=dscolors.indicator_bg, width=1)
            self._btnrecs.append(b)
        #Draw the hat display
        self._hatrecs = []
        rawpoints = [[(-hatsz, hatsz), (0, hatsz), (hatsz, hatsz)],
                     [(-hatsz, 0), (0, 0), (hatsz, 0)],
                     [(-hatsz, -hatsz), (0, -hatsz), (hatsz, -hatsz)]]
        hatlocs = [[(x+hatloc[0], y+hatloc[1]) for x, y in r] for r in rawpoints]
        for i in range(len(hatlocs)):
            self._hatrecs.append([])
            for x, y in hatlocs[i]:
                x0, y0, x1, y1 = x+xorg, y+yorg, x+xorg+hatsz, y+yorg+hatsz
                h = self._canvas.create_rectangle(x0, y0, x1, y1,
                    outline="black", fill=dscolors.indicator_bg, width=1)
                self._hatrecs[-1].append(h)
        self._hatrecs[0][0]
        #Set and draw the first zbar
        x, y, h, w = zbar1
        x0, y0, x1, y1 = xorg + x, yorg + y, xorg + x + w, yorg + y + h
        self._zbar1 = self._canvas.create_rectangle(x0, y0, x1, y1, outline="blue",
                            fill=dscolors.indicator_bg, width=linewidth)
        self._zdir1 = self._canvas.create_rectangle(x0+linewidth, y0+linewidth, 
                    x1-linewidth, y1-linewidth, fill=dscolors.indicator_fg, outline=dscolors.indicator_fg)
        #Set and draw the second zbar
        x, y, h, w = zbar2
        x0, y0, x1, y1 = xorg + x, yorg + y, xorg + x + w, yorg + y + h
        self._zbar2 = self._canvas.create_rectangle(x0, y0, x1, y1, outline="blue",
                            fill=dscolors.indicator_bg, width=linewidth)
        self._zdir2 = self._canvas.create_rectangle(x0+linewidth, y0+linewidth, 
                    x1-linewidth, y1-linewidth, fill=dscolors.indicator_fg, outline=dscolors.indicator_fg)
        self._statusfont = self._bigfont = tkFont.Font(family="Lucida Grande", size=10)
        x, y = textloc
        self._status = self._canvas.create_text(x + xorg, y + yorg, text="GamePad",
                        state=tk.DISABLED, fill="black", anchor=tk.CENTER, font=self._statusfont)
        self._joyaxis = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        self._joybtns = tuple([False for x in range(12)])
        self._joypov = (0, 0)
        self._lastaxis = None
        self._lastbtns = None
        self._lastpov = None
        self._lastmode = ''
        self._showaxes()
        self._showbtns()
        self._showpov()
  
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
            self.set_statustext(text="XBox Gamepad", color="black")
        if mode == 'invalid':
            self._canvas.itemconfig(self._background, fill=dscolors.indicator_invalid_bg,
                outline=dscolors.indicator_invalid_bg)
            self.set_statustext(text="XBox Gamepad Not Found", color="red")

    def set_axes(self, *args):
        ''' Sets the axis values.  Up to six floats can be given. 
        Axis values range from -1.0 to 1.0 '''
        if len(args) >= 6:
            self._joyaxis = args[:6]
        else:
            self._joyaxis = [0.0 for _ in range(6)]
            for i, v in enumerate(args):
                self._joyaxis[i] = v
        self._fixaxis()
        self._showaxes()

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

    def set_pov(self, pov):
        ''' Sets the pov hat states on the joystick display. A 2-tuple
        in the form (x,y) is expected, where x and y can be -1, 0, or 1.'''
        self._joypov = pov
        self._showpov()

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

    def _showaxes(self):
        ''' draws the position of the joystick on the diagram '''
        if self._joyaxis == self._lastaxis: return
        self._lastaxis = self._joyaxis
        for axis_num in range(2):
            if axis_num == 0:
                xorg_rel = a1xorg
                yorg_rel = a1yorg
                xdir = self._xdir1
                ydir = self._ydir1
                zdir = self._zdir1
                current_zbar = zbar1
                x, y, z, _, _, _ = self._joyaxis
                x = -x
            else:   # axis_num == 1:
                xorg_rel = a2xorg
                yorg_rel = a2yorg
                xdir = self._xdir2
                ydir = self._ydir2
                zdir = self._zdir2
                current_zbar = zbar2
                _, _, _, x, y, z = self._joyaxis
                x = -x
            ix, iy = xorg_rel - int(x * (barlen2-linewidth)), yorg_rel - int(y * (barlen2-linewidth))
            x0, y0, x1, y1 = xorg_rel, yorg_rel + barwidth2 - linewidth, ix, yorg_rel - barwidth2
            self._canvas.coords(xdir, x0, y0, x1, y1)
            x0, y0, x1, y1 = xorg_rel + barwidth2 - linewidth, yorg_rel, xorg_rel - barwidth2, iy
            self._canvas.coords(ydir, x0, y0, x1, y1)
            #Set zbar
            xx, yy, h, w = current_zbar
            iz = int(z * h)
            if iz < 1: iz = 1
            if iz > h-linewidth: iz = h-linewidth
            x0, y0 = xorg + xx + linewidth - 1, yorg + yy - linewidth + h
            x1, y1 = xorg + xx + w - linewidth, yorg + yy - linewidth + h - iz  
            self._canvas.coords(zdir, x0, y0, x1, y1)

    def _showbtns(self):
        ''' draws the conditions of the buttons on the diagram '''
        if self._joybtns == self._lastbtns: return
        self._lastbtns = self._joybtns
        for ir, r in enumerate(self._btnrecs):
            if self._joybtns[ir]:
                self._canvas.itemconfig(r, fill=dscolors.indicator_fg)
            else:
                self._canvas.itemconfig(r, fill=dscolors.indicator_bg)
    
    def _showpov(self):
        ''' draws the conditions of the pov hat on the diagram '''
        if self._joypov == self._lastpov: return
        self._lastpov = self._joypov
        for i in range(len(self._hatrecs)):
            for j in range(len(self._hatrecs[i])):
                if i == self._joypov[1]+1 and j == self._joypov[0]+1:
                    self._canvas.itemconfig(self._hatrecs[i][j], fill=dscolors.indicator_fg)
                else:
                    self._canvas.itemconfig(self._hatrecs[i][j], fill=dscolors.indicator_bg)
