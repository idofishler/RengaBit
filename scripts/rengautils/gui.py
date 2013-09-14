#!/usr/bin/env python

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

    def get_text(self):
        self.result = self.cmt.get('1.0', 'end')
        self.quit()

    def bring_to_front(self):
        self.lift()
        self.call('wm', 'attributes', '.', '-topmost', True)
        self.after_idle(self.call, 'wm', 'attributes', '.', '-topmost', False)

    def ask_for_comment(self):
        ttk.Label(self.mainframe, text="What changes did you make?").grid(
            column=2, row=0, sticky="W")
        ttk.Button(self.mainframe, text="OK", command=self.done).grid(
            column=3, row=2, sticky="W")
        self.cmt = Tkinter.StringVar()
        self.entry = ttk.Entry(self.mainframe, textvariable=self.cmt).grid(
            column=0, row=1, columnspan=4, sticky="EW")
        self.bind("<Return>", self.done())
        self.bring_to_front()

    def alert(self, msg):
        ttk.Label(self.mainframe, text=msg).grid(column=1, row=0, sticky="W")
        ttk.Button(self.mainframe, text="OK", command=self.quit).grid(
            column=3, row=1, sticky="W")
        self.bind("<Return>", self.quit())
        self.bring_to_front()

    def issue_report(self):
        info = 'Thanks for helping us improve RengaBit.\nPlease let us know what was the problem (short text is enough)\nIf you want us to contect you, sign with you name and email'
        ttk.Label(self.mainframe, text=info).grid(column=1, row=0, sticky="W")
        self.cmt = Tkinter.Text(self.mainframe, width=60, height=10)
        self.cmt.grid(column=0, row=2, columnspan=3)
        #self.entry = ttk.Entry(self.mainframe, textvariable=self.cmt).grid(column=0, row=2, columnspan=6, rowspan=4, sticky="EW")
        ttk.Button(self.mainframe, text="Send", command=self.get_text).grid(
            column=2, row=3, sticky="W")
        self.bring_to_front()

if __name__ == "__main__":
    app = RengaGui(None)
    app.mainloop()
