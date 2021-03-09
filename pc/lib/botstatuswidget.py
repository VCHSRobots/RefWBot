# botstatuswidget.py -- Widget to display the robot status
# EPIC Robotz, dlb, Mar 2021

import tkinter as tk  
import tkinter.font as tkFont
import dscolors

# Constants to control the layout of the diagram:
desiredsize = (125, 150) # desired size of widget for placing
horz_px, vert_px = 210, 150 # size of canvas
lineheight = 18 # height between fields
namewidth = 110  # size of the field name
xmargin = 2 # x margin for start of field name
fields = ("Bat1", "Bat2", "I2CErrs", "Restarts")

class BotStatusWidget(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent, borderwidth=2, relief="groove", bg=dscolors.widget_bg)
        self._canvas = tk.Canvas(self, width=horz_px, height=vert_px, borderwidth=0,
            highlightthickness=0, background=dscolors.widget_bg)
        self._canvas.pack(padx=2, pady=5)
        self._font1 = tkFont.Font(family="Lucida Grande", weight="bold", size=10)
        self._font2 = tkFont.Font(family="Lucida Grande", size=8)
        self._font3 = tkFont.Font(family="Lucida Grande", weight="bold", size=10)
        self._title = self._canvas.create_text(2, 7, anchor=tk.W, text="Bot Status",
                font=self._font1, fill="black")
        self._fields = []
        x, y = xmargin, 2*lineheight
        for name in fields:
            fname = self._canvas.create_text(x, y, anchor=tk.W, text=name+":", font=self._font2,
                fill=dscolors.label_black)
            fvalue = self._canvas.create_text(x + namewidth, y, anchor=tk.E, text="??.?",
                font=self._font3, fill="black")
            self._fields.append( (name, fname, fvalue) )
            y += lineheight
        
    def get_size(self):
        ''' Returns the desired size for this widget. '''
        return desiredsize

    def set_field(self, name, value):
        ''' Sets the value of a field on the display. '''
        for n, _ , fvalue in self._fields:
            if n == name:
                self._canvas.itemconfig(fvalue, text=value)
                return


