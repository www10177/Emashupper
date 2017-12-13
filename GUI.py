from Tkinter import *
from library import pre
from pandas import read_csv
import os


PgzLocation = '../pgz'
WavLocation = '../wav'

class Application(Frame):

    def __init__(self,parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.parent.title = "AutoMashupper"
        self.initUI()

    def initUI(self):
        self.pack(fill=BOTH, expand=1)
        self.label()
        self.listbox()


    def label(self):
        Label( self, textvariable=StringVar(value='pgz location : ' + PgzLocation)).grid( row=0, column=1, columnspan=30, pady=5, sticky=W)

    def listbox(self):
        self.songlist = Listbox(self)
        csv = read_csv(os.path.join(PgzLocation , 'metadata.csv'))
        for song in csv['song name']:
            self.songlist.insert(END,song)


root = Tk()
size = 860, 640
app = Application(root)
root.geometry('860x640')
root.mainloop()
root.destroy()
