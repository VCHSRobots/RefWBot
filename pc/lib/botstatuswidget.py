# botstatuswidget.py -- Widget to display the robot status
# EPIC Robotz, dlb, Mar 2021

import tkinter as tk  
import tkinter.font as tkFont
import dscolors

# Constants to control the layout of the diagram:
desiredsize = (120, 150) # desired size of widget for placing
horz_px, vert_px = 120, 150 # size of canvas
lineheight = 18 # height between fields
namewidth = 105  # size of the field name
xmargin = 2 # x margin for start of field name
loc_rstbtn = (55, 123)
fields = ("Bat M", "Bat L", "I2CErrs", "Recovers", "CodeVer")

class BotStatusWidget(tk.Frame):
    def __init__(self, parent, reset_callback=None):
        tk.Frame.__init__(self, parent, borderwidth=2, relief="groove", bg=dscolors.widget_bg)
        self._resetcb = None
        self._canvas = tk.Canvas(self, width=horz_px, height=vert_px, borderwidth=0,
            highlightthickness=0, background=dscolors.widget_bg)
        #self._canvas.pack(padx=2, pady=5)
        self._canvas.place(x=0, y=5, width=horz_px-10, height=vert_px-10)
        self._smfont = tkFont.Font(family="Lucida Grande", size=6)
        self._rstbtn = tk.Button(self, text="Reset Arduino", 
            font=self._smfont, width=8, bg=dscolors.button_bg, command=self._on_reset)
        x, y = loc_rstbtn
        self._rstbtn.place(x=x, y=y)
        self._resetcb = reset_callback
        self._font1 = tkFont.Font(family="Lucida Grande", weight="bold", size=10)
        self._font2 = tkFont.Font(family="Lucida Grande", size=8)
        self._font3 = tkFont.Font(family="Lucida Grande", weight="bold", size=10)
        self._title = self._canvas.create_text(2, 7, anchor=tk.W, text="Bot Status",
                font=self._font1, fill="black")
        self._fields = []
        x, y = xmargin, int(1.7*lineheight)
        for name in fields:
            fname = self._canvas.create_text(x, y, anchor=tk.W, text=name+":", font=self._font2,
                fill=dscolors.label_black)
            fvalue = self._canvas.create_text(x + namewidth, y, anchor=tk.E, text="??.?",
                font=self._font3, fill="black")
            self._fields.append( (name, fname, fvalue) )
            y += lineheight
        
    def _on_reset(self):
        ''' Reset the arduino.'''
        if self._resetcb: self._resetcb()

    def get_size(self):
        ''' Returns the desired size for this widget. '''
        return desiredsize

    def set_field(self, name, value):
        ''' Sets the value of a field on the display. '''
        for n, _ , fvalue in self._fields:
            if n == name:
                self._canvas.itemconfig(fvalue, text=value)
                return


