#! /usr/bin/env python

import Tkinter
import ttk


class RengaGui(Tkinter.Tk):

    def __init__(self, parent):
        Tkinter.Tk.__init__(self, parent)
        self.parent = parent
        self.title('RengaBit')
        self.mainframe = ttk.Frame(self, padding="3 3 12 12")
        self.mainframe.grid(column=0, row=0, sticky="NWSE")
        self.mainframe.columnconfigure(0, weight=2)
        self.mainframe.rowconfigure(0, weight=1)
        self.resizable(False, False)

    def done(self, event=None):
        self.result = self.cmt.get()
        self.quit()

    def ask_for_comment(self):
        ttk.Label(self.mainframe, text="What changes did you make?").grid(column=2, row=0, sticky="W")
        ttk.Button(self.mainframe, text="OK", command=self.done).grid(column=3, row=2, sticky="W")
        self.cmt = Tkinter.StringVar()
        self.entry = ttk.Entry(self.mainframe, textvariable=self.cmt).grid(column=0, row=1, columnspan=4, sticky="EW")
        self.bind("<Return>", self.done())

if __name__ == "__main__":
    app = RengaGui(None)
    app.mainloop()
