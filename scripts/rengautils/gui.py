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
        self.font = ('Open Sans', 13)

    def center(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() / 2) - (width / 2)
        y = (self.winfo_screenheight() / 2) - (height / 2)
        self.geometry('{0}x{1}+{2}+{3}'.format(width, height, x, y))

    def done(self, event=None):
        self.result = self.cmt.get()
        self.quit()

    def get_text(self):
        self.result = self.cmt.get('1.0', 'end')
        self.quit()

    def bring_to_front(self):
        self.center()
        self.lift()
        self.call('wm', 'attributes', '.', '-topmost', True)
        self.after_idle(self.call, 'wm', 'attributes', '.', '-topmost', False)

    def ask_for_comment(self):
        ttk.Label(self.mainframe, font=self.font, text="What changes did you make?").grid(
            column=2, row=0, sticky="W")
        ttk.Button(self.mainframe, text="OK", command=self.done).grid(
            column=3, row=2, sticky="W")
        self.cmt = Tkinter.StringVar()
        self.entry = ttk.Entry(
            self.mainframe, font=self.font, textvariable=self.cmt)
        self.entry.grid(column=0, row=1, columnspan=4, sticky="EW")
        self.entry.focus_set()
        self.entry.bind("<Return>", lambda e: self.done())
        self.bring_to_front()

    def alert(self, msg):
        ttk.Label(self.mainframe, font=self.font, text=msg).grid(
            column=1, row=0, sticky="W")
        button = ttk.Button(self.mainframe, text="OK", command=self.quit)
        button.grid(column=3, row=1, sticky="W")
        button.focus_set()
        button.bind("<Return>", lambda e: self.quit())
        self.bring_to_front()

    def issue_report(self):
        info = '''Thanks for helping us improve RengaBit.
Please let us know what was the problem (short text is enough)
If you want us to contect you, sign with you name and email'''
        ttk.Label(self.mainframe, font=self.font, text=info).grid(
            column=0, row=0, sticky="W")
        self.cmt = Tkinter.Text(
            self.mainframe, font=self.font, width=60, height=10)
        self.cmt.grid(column=0, row=2, columnspan=3)
        self.cmt.focus_set()
        button = ttk.Button(self.mainframe, text="Send", command=self.get_text)
        button.grid(column=2, row=3, sticky="W")
        self.bring_to_front()

if __name__ == "__main__":
    app = RengaGui(None)
    app.mainloop()
