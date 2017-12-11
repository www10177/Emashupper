from Tkinter import *
import tkFileDialog
from library import pre


class Application(Frame):

    def __init__(self, master=None):
        # init parameter
        self.pgzFolder = '../pgz'
        self.rawFolder = '../wav'
        Frame.__init__(self, master, relief=SUNKEN, bd=2)
        self.master.title = "AutoMashupper"
        self.label()


    def label(self):
        Label( self, textvariable=self.pgzFolder).grid( row=0, column=1, columnspan=10, pady=5, sticky=W)


root = Tk()
size = 860, 640
app = Application(root)
root.geometry('860x640')
root.mainloop()
root.destroy()
print type(size)
