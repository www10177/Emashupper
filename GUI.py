# -*- coding:utf-8 -*-
from sys import platform as sys_pf
if sys_pf == 'darwin':
    import matplotlib
    matplotlib.use("TkAgg")

from Tkinter import *
from lib import pre
from pandas import read_csv
import os
from subprocess import call,Popen
import numpy as np
import matplotlib.pyplot as plt
import librosa.display


PgzLocation = '../pgz'
WavLocation = '../wav_seg'

class Application(Frame):

    def __init__(self,parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.initVar()
        self.initUI()
    
    def initVar(self):
        # initialize public variable
        self.csv = read_csv(os.path.join(PgzLocation , 'metadata.csv'))
        self.seedIndex= -1
        self.seedSegCount=-1
        self.seedName = ''
        self.seed = [None] * self.seedSegCount #PreAudio list of seed song
        self.mashup= [None]*self.seedSegCount #PreAudio list of selected candidated song

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
        self.seedIndex = index
        self.seedName = value
        print 'selected %d: "%s"' % (index, value)

    def listbox(self):
        # show all song list
        self.songlist = Listbox(self,selectmode=SINGLE)
        for song in self.csv['song name']:
            self.songlist.insert(END,song)
        self.songlist.config(width=0)
        self.songlist.grid(row=1,column=1,rowspan=10,sticky='NSWE')
        self.songlist.bind('<<ListboxSelect>>', self.onselect)


    def load(self):
        self.seedSegCount= self.csv['segmentation count'][self.seedIndex]
        self.seed = [None] * self.seedSegCount
        for i in xrange(0,self.seedSegCount):
            name = os.path.join(PgzLocation,self.seedName+'_'+str(i+1)+'.pgz')
            self.seed[i] = pre.load(name)
            print 'loaded ',self.seed[i].name

    def seedShow(self):
        signal = self.seed[0].signal
        for i in self.seed[1:]:
            print i.name
            signal = np.concatenate((signal,i.signal))
        librosa.display.waveplot(signal, sr=self.seed[0].sr)
        plt.title('Seed Wave')
        plt.show()

    def playSeed(self):
        if sys.platform == 'darwin':
            Popen(["afplay",os.path.join(WavLocation,self.seedName+'_1.wav')])

    def mashupSong(self):
        self.mashup= [None]*self.seedSegCount
        for seedSegNow in xrange(0,self.seedSegCount):
        # iterate all segmentations in seed song
            maxMashability = -1000
            candSeg=None
            maxSeg =None
            for candIndex,candName in enumerate(self.csv['song name']):
            # iterate all songs in database
                if candIndex == self.seedIndex:
                    continue
                for candSegIndex in xrange(1,self.csv['segmentation count'][candIndex]+1):
                # iterate all segmentations in candidate song
                    candSegPath = os.path.join(PgzLocation,candName+'_'+str(candSegIndex)+'.pgz')
                    candSeg = pre.load(candSegPath)
                    mash = pre.Mashability(self.seed[seedSegNow], candSeg).mash()
                    if maxMashability < mash:
                        maxMashability = mash
                        maxSeg = candSeg
                print 'compared :',candName
                if maxSeg is not None:
                    print 'maxSeg = ',maxSeg.name
            print 'Mashed : #',seedSegNow+1 ,' of ', self.seedSegCount
            self.mashup[seedSegNow] =maxSeg 
        print 'selected : '
        for i in self.mashup:
            print i.name

    def saveMashuped(self):
    # !!WARNING!! Only saved candidate song, need to add seed song together !!WARNING!!
        signal = self.mashup[0].signal
        print len(self.mashup)
        for i in self.mashup[1:]:
            signal = np.concatenate((signal,i.signal))
        librosa.output.write_wav('./mashuped.wav',signal,self.seed[0].sr)
    def playMashuped(self):
        self.saveMashuped()
        if sys.platform == 'darwin':
            Popen(["afplay",'./mashuped.wav'])
    def showMashuped(self):
        signal = self.mashup[0].signal
        for i in self.mashup[1:]:
            signal = np.concatenate((signal,i.signal))
        librosa.display.waveplot(signal, sr=self.seed[0].sr)
        plt.title('Mashuped Wave')
        plt.show()

        
    def actionElements(self):
        # initialze buttons,labels...
        Button(self,text='-> Load ',command=self.load).grid(row=1,column=2,sticky='WE')
        Label(self,text="---------Seed---------").grid(row=2,column=2,sticky='WE')
        Button(self,text='Play Seed Song',command=self.playSeed).grid(row=3,column=2,sticky='WE')
        Button(self,text='Show Seed Wave',command=self.seedShow).grid(row=4,column=2,sticky='WE')
        Label(self,text="---------Mash---------").grid(row=5,column=2,sticky='WE')
        Button(self,text='*Mashup*',command=self.mashupSong).grid(row=6,column=2,sticky='WE')
        Button(self,text='Play Mashuped Song',command=self.playMashuped).grid(row=7,column=2,sticky='WE')
        Button(self,text='Show Mashuped Wave',command=self.showMashuped).grid(row=8,column=2,sticky='WE')
        Button(self,text='<- Save Mashuped Song',command=self.saveMashuped).grid(row=9,column=2,sticky='WE')


if __name__ == '__main__':
    print 'pgz : ', PgzLocation
    print 'wav : ', WavLocation
    root = Tk()
    app = Application(root)
    root.geometry('640x480')
    root.mainloop()
    root.destroy()
