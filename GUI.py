from Tkinter import *
from lib import pre
from pandas import read_csv
import os


PgzLocation = '../pgz'
WavLocation = '../wav'

class Application(Frame):

    def __init__(self,parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.initVar()
        self.initUI()
    
    def initVar(self):
        # initialize public variable
        self.csv = read_csv(os.path.join(PgzLocation , 'metadata.csv'))
        self.songIndex= -1
        self.songName = ''

    def initUI(self):
        #initialize UI
        self.parent.title("AutoMashupper")
        self.pack(fill=BOTH,expand=1)
        self.listbox()
        self.actionElements()

    def onselect(self, evt):
        # event helper for listbox slection
        # Note here that Tkinter passes an event object to onselect()
        w = evt.widget
        index = int(w.curselection()[0])
        value = w.get(index)
        self.songIndex = index
        self.songName = value
        print 'selected %d: "%s"' % (index, value)

    def listbox(self):
        # show all song list
        self.songlist = Listbox(self,selectmode=SINGLE)
        for song in self.csv['song name']:
            self.songlist.insert(END,song)
        self.songlist.config(width=0)
        self.songlist.grid(row=1,column=1,rowspan=10,sticky='NSWE')
        self.songlist.bind('<<ListboxSelect>>', self.onselect)

    def actionElements(self):
        # initialze buttons,labels...

        Button(self,text='-> Load ').grid(row=1,column=2,sticky='WE')
        Label(self,text="---------Seed---------").grid(row=2,column=2,sticky='WE')
        Button(self,text='Play Seed Song').grid(row=3,column=2,sticky='WE')
        Button(self,text='Show Seed Wave').grid(row=4,column=2,sticky='WE')
        Label(self,text="---------Mash---------").grid(row=5,column=2,sticky='WE')
        Button(self,text='*Mashup*').grid(row=6,column=2,sticky='WE')
        Button(self,text='Play Mashuped Song').grid(row=7,column=2,sticky='WE')
        Button(self,text='Show Mashuped Wave').grid(row=8,column=2,sticky='WE')
        Button(self,text='<- Save Mashuped Song').grid(row=9,column=2,sticky='WE')


if __name__ == '__main__':
    print 'pgz : ', PgzLocation
    print 'wav : ', WavLocation
    root = Tk()
    app = Application(root)
    root.geometry('860x640')
    root.mainloop()
    root.destroy()
