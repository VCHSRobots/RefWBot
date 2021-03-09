# hardwarestatuswidget.pc -- Widget to display hardware status
# EPIC Robotz, dlb, Mar 2021

import tkinter as tk  
import tkinter.font as tkFont
import dscolors

# Constants to control the layout of the diagram:
desiredsize = (250, 85) # desired size of widget for placing
horz_px, vert_px = 215, 85 # size of canvas
boxsize = (25, 15) # size of the rect box for the lights
boxpad = 10
boxes = ((1, 0, "Joystick"), (1, 25, "Comm"), (1, 50, "Code"),
         (120, 0, "I2C Bus"), (120, 25, "Bat M"), (120, 50, "Bat L"))
linewidth = 2

class HardwareStatusWidget(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent, borderwidth=2, relief="groove", bg=dscolors.widget_bg)
        self._canvas = tk.Canvas(self, width=horz_px, height=vert_px, borderwidth=0,
            highlightthickness=0, background=dscolors.widget_bg)
        self._canvas.pack(padx=1, pady=5)
        self._font = tkFont.Font(family="Lucida Grande", weight="bold", size=12)
        self._boxes = []
        for x, y, name in boxes:
            w, h = boxsize
            x0, y0, x1, y1 = x, y, x + w, y + h 
            r = self._canvas.create_rectangle(x0, y0, x1, y1, outline="black",
                fill=dscolors.indicator_bg, width=linewidth)
            x0, y0 = x + w + boxpad, y + h
            t = self._canvas.create_text(x0, y0 - 6, text=name, font=self._font, 
                fill="black", anchor=tk.W)
            self._boxes.append((r, t, name))

    def get_size(self):
        ''' Returns the desired size for this widget. '''
        return desiredsize

    def set_status(self, boxname, color):
        ''' Sets the status color of a box.  The color can be a named color
        or a hex number in the form of x0rrggbb. '''
        for r, _, name in self._boxes:
            if name == boxname: 
                self._canvas.itemconfig(r, fill=color)
                return