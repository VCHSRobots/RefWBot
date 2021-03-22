# joystickwidget_logitech.py -- joystick widget to show joystick inputs 
# for Logitech Extreme 3D Pro Joystick
# EPIC Robotz, dlb, Mar 2021

import tkinter as tk
import tkinter.font as tkFont
import math

# Constants to control the layout of the diagram:
desiredsize = (250, 230) # desired size of widget for placing
horz_px = 210 # horzontal size of the the widget in pixels
vert_px = 210 # vertial size of the widget in pixels
blockout = (0, 0, 200, 180) # block out rect for invalid flag
xorg = 100 # x orgin of the complete diagram. which is center of main cross bars.
yorg = 100 # y orgin of the complete diagram, which is center of main cross bars.
a1xorg = 50 # x origin of the right cross bars
a1yorg = 100 # y origin of the right cross bars
a2xorg = 150 # x origin of the left cross bars
a2yorg = 130 # y origin of the right cross bars
zbar1 = (-80, 30, 50, 10) # loc, len, width of the first z slider diagram
zbar2 = (80, 50, 50, 10) # loc, len, width of the second z slider diagram
textloc = (0, 90) # center loc of the status text
hatloc = (-40, 60) # center loc of the hats indicator
barlen2 = 40   # one side bar lenght in px
barwidth2 = 8  # one half of bar width in px
linewidth = 2   # linewidth on edges of bars and buttons
btnsz = 8  # size of the buttons in px
hatsz = 8
# locations of buttons relative to orgin
btnrectslocs=((75, -25), (83, -33), (67, -33), (75, -41), (-60, -75), (60, -75), 
              (-35, -50), (35, -50), (0, -50), (-55, -2), (45, 28))

class JoystickWidget(tk.Frame):
    def __init__(self, parent):
        #Create main tk frame
        tk.Frame.__init__(self, parent, borderwidth=2, relief="groove", bg="white")
        self._canvas = tk.Canvas(self, width=horz_px, height=vert_px, borderwidth=0,
            highlightthickness=0, background='white')
        self._canvas.pack(padx=10, pady=10)
        self._background = self._canvas.create_rectangle(*blockout, fill="", outline="")
        rawpoints = [(-barwidth2, barwidth2),
            (-barwidth2, barwidth2), (-barwidth2, barlen2), (barwidth2, barlen2),
            (barwidth2, barwidth2), (barlen2, barwidth2), (barlen2, -barwidth2),
            (barwidth2, -barwidth2), (barwidth2, -barlen2), (-barwidth2, -barlen2),
            (-barwidth2, -barwidth2), (-barlen2, -barwidth2), (-barlen2, barwidth2),
            (-barwidth2, barwidth2)]
        #Draw the pirst cross display
        relpoints = [(x+a1xorg, y+a1yorg) for x,y in rawpoints]       
        self._canvas.create_polygon(relpoints, outline="blue", fill="lightgrey", width=linewidth)
        self._xdir1 = self._canvas.create_rectangle(a1xorg-linewidth, a1yorg+(barwidth2-linewidth),
            a1xorg+linewidth, yorg-(barwidth2-linewidth), fill="red", outline="red")
        self._ydir1 = self._canvas.create_rectangle(a1xorg-(barwidth2-linewidth), a1yorg-linewidth,
            a1xorg+(barwidth2-linewidth), a1yorg+linewidth, fill="red", outline="red")
        self._dot1 = self._canvas.create_oval(a1xorg-(barwidth2-linewidth), a1yorg-(barwidth2-linewidth),
            a1xorg+(barwidth2-linewidth), a1yorg+(barwidth2-linewidth), fill="red", outline="red")
        #Draw the second cross display
        relpoints = [(x+a2xorg, y+a2yorg) for x,y in rawpoints]       
        self._canvas.create_polygon(relpoints, outline="blue", fill="lightgrey", width=linewidth)
        self._xdir2 = self._canvas.create_rectangle(a2xorg-linewidth, a2yorg+(barwidth2-linewidth),
            a2xorg+linewidth, a2yorg-(barwidth2-linewidth), fill="red", outline="red")
        self._ydir2 = self._canvas.create_rectangle(a2xorg-(barwidth2-linewidth), a2yorg-linewidth,
            a2xorg+(barwidth2-linewidth), a2yorg+linewidth, fill="red", outline="red")
        self._dot2 = self._canvas.create_oval(a2xorg-(barwidth2-linewidth), a2yorg-(barwidth2-linewidth),
            a2xorg+(barwidth2-linewidth), a2yorg+(barwidth2-linewidth), fill="red", outline="red")
        #Draw the buttons
        self._btnrecs = []
        for x, y in btnrectslocs: 
            x0, y0, x1, y1 = x+xorg, y+yorg, x+xorg+btnsz, y+yorg+btnsz
            b = self._canvas.create_rectangle(x0, y0, x1, y1,
                outline="black", fill="lightgray", width=1)
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
                    outline="black", fill="lightgray", width=1)
                self._hatrecs[-1].append(h)
        self._hatrecs[0][0]
        #Set and draw the first zbar
        x, y, h, w = zbar1
        x0, y0, x1, y1 = xorg + x, yorg + y, xorg + x + w, yorg + y + h
        self._zbar1 = self._canvas.create_rectangle(x0, y0, x1, y1, outline="blue",
                            fill="lightgray", width=linewidth)
        self._zdir1 = self._canvas.create_rectangle(x0+linewidth, y0+linewidth, 
                    x1-linewidth, y1-linewidth, fill="red", outline="red")
        #Set and draw the second zbar
        x, y, h, w = zbar2
        x0, y0, x1, y1 = xorg + x, yorg + y, xorg + x + w, yorg + y + h
        self._zbar2 = self._canvas.create_rectangle(x0, y0, x1, y1, outline="blue",
                            fill="lightgray", width=linewidth)
        self._zdir2 = self._canvas.create_rectangle(x0+linewidth, y0+linewidth, 
                    x1-linewidth, y1-linewidth, fill="red", outline="red")
        self._statusfont = self._bigfont = tkFont.Font(family="Lucida Grande", size=12)
        x, y = textloc
        self._status = self._canvas.create_text(x + xorg, y + yorg, text="Joystick",
                        state=tk.DISABLED, fill="black", anchor=tk.CENTER, font=self._statusfont)
        self._joyaxis = (0.0, 0.0, 0.0)
        self._joybtns = tuple([False for x in range(12)])
        self._joyhats = (0, 0)
        self._lastaxis = None
        self._lastbtns = None
        self._lasthats = None
        self._lastmode = ''

        self._showaxes()
        self._showbtns()
        self._showhats()
  
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
            self._canvas.itemconfig(self._background, fill="", outline="")
            self.set_statustext(text="Joystick", color="black")
        if mode == 'invalid':
            self._canvas.itemconfig(self._background, fill="yellow", outline="yellow")
            self.set_statustext(text="Joystick Not Found", color="red")

    def set_axis(self, *args, axis=0):
        ''' Sets the axis values for x, y, z directions. 0-3 values can be given.
        Axis values range from -1.0 to 1.0 '''
        if len(args) >= 3:
            self._joyaxis = args[:4]
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
        self._showaxes(axis=axis)

    def set_ruv(self, *args):
        ''' Redirect to set_axis function '''
        self.set_axis(args, axis=1)

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

    def set_hats(self, *hats):
        ''' Sets the hat states on the joystick display.
        2 booleans and/or integers can be provided. '''
        if len(hats) < 2:
            return
        self._joyhats = tuple(hats[:2])
        self._showhats()

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

    def _showaxes(self, axis=0):
        ''' draws the position of the joystick on the diagram '''
        if self._joyaxis == self._lastaxis: return
        self._lastaxis = self._joyaxis
        if axis==0:
            xorg_rel = a1xorg
            yorg_rel = a1yorg
            xdir = self._xdir1
            ydir = self._ydir1
            zdir = self._zdir1
            current_zbar = zbar1
        elif axis==1:
            xorg_rel = a2xorg
            yorg_rel = a2yorg
            xdir = self._xdir2
            ydir = self._ydir2
            zdir = self._zdir2
            current_zbar = zbar2
        else:
            xorg_rel = xorg
            yorg_rel = yorg
            xdir = self._xdir1
            ydir = self._ydir1
            zdir = self._zdir1
            current_zbar = zbar1
        x, y, z = self._joyaxis
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
        icnt = 0
        for r in self._btnrecs:
            if self._joybtns[icnt]:
                self._canvas.itemconfig(r, fill="red")
            else:
                self._canvas.itemconfig(r, fill="lightgray")
            icnt += 1
    
    def _showhats(self):
        ''' draws the conditions of the hats on the diagram '''
        if self._joyhats == self._lasthats: return
        self._lasthats = self._joyhats
        for i in range(len(self._hatrecs)):
            for j in range(len(self._hatrecs[i])):
                if i == self._joyhats[1]+1 and j == self._joyhats[0]+1:
                    self._canvas.itemconfig(self._hatrecs[i][j], fill="red")
                else:
                    self._canvas.itemconfig(self._hatrecs[i][j], fill="lightgray")
