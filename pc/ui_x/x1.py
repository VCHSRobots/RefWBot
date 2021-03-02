# x1.py -- ui experiment 1 -- create a window, with a frame/canvas.
# EPIC Robotz, dlb, Mar 2021

import tkinter as tk
import gameclockwidget

class CustomWidget(tk.Frame):
    def __init__(self, parent, label, default=""):
        tk.Frame.__init__(self, parent)

        self.left_frame = tk.Frame(self)
        self.right_frame = tk.Frame(self)
        self.left_frame.pack(side="left", fill="x")
        self.right_frame.pack(side="right")

        self.drawing_surface = tk.Canvas(self.right_frame, width=100, height=50,
                borderwidth=0, highlightthickness=0, background='white')
        self.drawing_surface.pack(padx=10, pady=10)
        self.drawing_surface.create_rectangle(10, 10, 50, 20)

        self.label = tk.Label(self.left_frame, text=label, anchor="w")
        self.entry = tk.Entry(self.left_frame)
        self.entry.insert(0, default)
        self.label.pack(side="top", fill="x")
        self.entry.pack(side="bottom", fill="x", padx=4)

    def get(self):
        return self.entry.get()

class MonitorWidget():
    def __init__(self, wg, name):
        self.wg = wg
        self.name = name
        self.wg.bind("<Configure>", self.on_configure)
        self.wg.bind("<Button>", self.on_button)

    def on_configure(self, e):
        print("<Configure> Event on Widget %s. Width,Height = (%d, %d)" % (self.name, e.width, e.height))

    def on_button(self, e):
        print("<Button> Event on Widget %s. x, y = (%d, %d)" % (self.name, e.x, e.y))


class Example(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.label = tk.Label(self)
        self.e1 = CustomWidget(self, "First Name:", "Inigo")
        self.e2 = CustomWidget(self, "Last Name:", "Montoya")
        self.submitButton = tk.Button(self, text="Submit", command=self.submit)
        self.status_label = tk.Label(self, text="??")

        self.e1_mon = MonitorWidget(self.e1, "e1")
        self.e2_mon = MonitorWidget(self.e2, "e2")

        self.gc = gameclockwidget.GameClockWidget(self)

        #self.e1.grid(row=0, column=0, sticky="ew")
        #self.e2.grid(row=1, column=0, sticky="ew")
        #self.label.grid(row=2, column=0, sticky="ew")
        #self.submitButton.grid(row=4, column=0)

        self.e1.place(x=10, y=30)
        self.e2.place(x=10, y=90)
        self.label.place(x=10, y=0)
        self.submitButton.place(x=50, y=160)
        self.gc.place(x=40, y=200)
        self.status_label.place(x=10, y=600)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.changecount = 0
        self.bind("<Configure>", self.monitor_changes)

    def monitor_changes(self, event):
        self.changecount += 1
        x,y,w,h = event.x, event.y, event.width, event.height
        print("monitor_changes called. %d, x=%d, y=%d, width=%d, height=%d." % (self.changecount, x, y, w, h))
        self.saysize()

    def submit(self):
        self.saysize()
        first = self.e1.get()
        last = self.e2.get()
        self.label.configure(text="Hello, %s %s" % (first, last))

    def saysize(self):
        x, y = self.winfo_width(), self.winfo_height()
        self.status_label.configure(text="%d, %d" % (x, y))


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Driver Station for Water Bot")
    root.geometry('300x900')
    x1 = Example(root)
    x1.place(x=0, y=0, relwidth=1, relheight=1)
    x1.saysize()
    root.mainloop()