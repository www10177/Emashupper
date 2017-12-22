# -*- coding:utf-8 -*-
from sys import platform as sys_pf
if sys_pf == 'darwin':
    import matplotlib
    matplotlib.use("TkAgg")

from Tkinter import *
from lib import pre, mashup
from pandas import read_csv
import os
from subprocess import call,Popen
import numpy as np
import pygame
import matplotlib.pyplot as plt
import librosa.display

from PyQt4.QtGui import *

SongPgzLocation = '../normalized_pgz/song'
PgzLocation = '../normalized_pgz/inst'
WavLocation = '../normalized_wavSeg/inst'

LoadMode = 1
# 0 would load pgz seperately, which might be slower but use less memory
# 1 would load all pgz at once, which might be faster but use more memory

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
        self.mashup = [None] * self.seedSegCount #PreAudio list of selected candidated song
        self.mashuppedSig = None

    def initUI(self):
        #initialize UI
        self.parent.title("Emashupper")
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
            name = os.path.join(PgzLocation,'normalized-'+self.seedName+'(inst)'+'_'+str(i+1)+'.pgz')
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
            Popen(["afplay",os.path.join(WavLocation,'normalized-'+self.seedName+'(inst)'+ '_1.wav')])

    def mashupLoadAtOnce(self):
        self.mashup = [None]*self.seedSegCount
        mashabilityList = [None]*self.seedSegCount
        mashupedIndex = [] # saved already mashuped seg index to filter repeat
        threshold = 0.82
        seg = []

        # load all segmentation
        for candIndex,candName in enumerate(self.csv['song name']):
            if candIndex == self.seedIndex:
                continue
            for candSegIndex in xrange(1,self.csv['segmentation count'][candIndex]+1):
                candSegPath = os.path.join(PgzLocation,'normalized-'+candName+'(inst)'+'_'+str(candSegIndex)+'.pgz')
                seg.append(pre.load(candSegPath))
        print "loaded all seg"

        #Mashupping
        for seedSegNow in xrange(0,self.seedSegCount):
        # iterate all segmentations in seed song
        
            # Notice: The first section and the last section will not be mashupped.
            if seedSegNow == 0 or seedSegNow == self.seedSegCount-1 :
                continue
            
            maxMashability = -1000
            maxSeg = None
            maxIndex = -1 
            for segIndex ,cand in enumerate(seg):
            # iterate all segmentation
                mash = pre.Mashability(self.seed[seedSegNow], cand).mash()
                if maxMashability < mash:
                    maxMashability = mash
                    maxSeg = cand
                    maxIndex = segIndex
                if segIndex % 10  == 0:
                    print 'compared : ',segIndex, ' of ' ,len(seg) 
            print 'maxSeg = ',maxSeg.name
            mashabilityList[seedSegNow] = maxMashability
            candWithVocalSegPath = os.path.join(SongPgzLocation,maxSeg.name[:maxSeg.name.rfind('(inst')]+maxSeg.name[maxSeg.name.rfind('_'):]+'.pgz')
            print 'Mashed File: '+ maxSeg.name[:maxSeg.name.rfind('(inst')]+maxSeg.name[maxSeg.name.rfind('_'):]+'.pgz'
            
            if maxMashability >= threshold :
                self.mashup[seedSegNow] = pre.load(candWithVocalSegPath)
            else: print('Mashability < Threshold , Skip ...')

            print 'Mashed : #',seedSegNow+1 ,' of ', self.seedSegCount
            
            del seg[maxIndex]
            
        print 'selected : '
        for index, candSeg in enumerate(self.mashup):
            if candSeg :
                print candSeg.name,' : ', mashabilityList[index]
        self.saveMashuped()

    def mashupLoadSeperately(self):
        self.mashup= [None]*self.seedSegCount
        mashabilityList = [None]*self.seedSegCount
        mashupedDic={}
        threshold = 0.82
        for seedSegNow in xrange(0,self.seedSegCount):
        # iterate all segmentations in seed song
            maxMashability = -1000
            candSeg = None
            maxSeg = None
            for candIndex,candName in enumerate(self.csv['song name']):
            # iterate all songs in database
                if candIndex == self.seedIndex :
                    continue
                for candSegIndex in xrange(1,self.csv['segmentation count'][candIndex]+1):
                # iterate all segmentations in candidate song
                    candSegPath = os.path.join(PgzLocation,candName+'_'+str(candSegIndex)+'.pgz')
                    if canSedPath[:-4] in mashupedDic:
                        print canSedPath, ' is already mashupped '
                        continue
                    candSeg = pre.load(candSegPath)
                    mash = pre.Mashability(self.seed[seedSegNow], candSeg).mash()
                    if maxMashability < mash:
                        maxMashability = mash
                        maxSeg = candSeg
                print 'compared :',candName
                if maxSeg is not None:
                    print 'maxSeg = ',maxSeg.name
                    mashabilityList[seedSegNow] = maxMashability
            print 'Mashed : #',seedSegNow+1 ,' of ', self.seedSegCount
            
            if maxMashability >= threshold :
                self.mashup[seedSegNow] = maxSeg
            else: print('Mashability < Threshold , Skip...')
            
            mashupedDic.add({maxSeg.name:True})
        print 'selected : '
        for index, candSeg in enumerate(self.mashup):
            print candSeg.name,' : ', mashabilityList[index]
        self.saveMashuped()

    def mashupSong(self):
        if LoadMode == 0:
            print 'Load canidate seperately'
            self.mashupLoadSeperately()
        elif LoadMode == 1:
            print 'Load canidate at once'
            self.mashupLoadAtOnce()

    def saveMashuped(self):
        seg = [None] * self.seedSegCount
        for i in xrange(self.seedSegCount):
            if self.mashup[i] :
                seg[i] = mashup.overlay(self.mashup[i].signal, self.mashup[i].sr, self.seed[i].signal, self.seed[i].sr)
            ############ TO DO: matching the beats
            else :
                seg[i] = self.seed[i].signal
            
            if i == 0 :
                signal = seg[i]
            else:
                signal = mashup.bridging(signal, self.seed[0].sr,seg[i], self.seed[0].sr)
        
        outputFile = './'+"".join(self.seedName.strip().split(' '))+'_mashupped.wav'
        librosa.output.write_wav(outputFile,signal,self.seed[0].sr)
        mashup.volume_adjust(outputFile)
        self.mashuppedSig = signal
        print ('Done processing mashupped song.')
            
    def playMashuped(self):
        self.saveMashuped()
        if sys.platform == 'darwin':
            Popen(["afplay",'./normalized-'+"".join(self.seedName.strip().split(' '))+'_mashupped.wav'])

    def showMashuped(self):
        if self.mashuppedSig :
            librosa.display.waveplot(self.mashuppedSig, sr=self.seed[0].sr)
            plt.title('Mashupped Wave')
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
    print 'pgz(inst) : ', PgzLocation
    print 'pgz(song) : ', SongPgzLocation
    print 'wav : ', WavLocation
    
    app = QApplication(sys.argv)
    widget = QWidget()
    widget.resize(1280, 720)
    widget.move(80, 0)
    widget.setWindowTitle("Emashupper")

    loadFile = QPushButton("Load")
    playSeed = QPushButton("Play Seed Song")
    showSeed = QPushButton("Show Seed Wave")
    
    
    
    ok = QPushButton("&Load")
    cancel = QPushButton("&Cancel")
    #cancel.clicked.connect(button.close)
    
    layout = QHBoxLayout()
    layout.addWidget(ok)
    layout.addWidget(cancel)

#    lineEdit = QLineEdit()
#    go = QPushButton("&GO")
#    h1 = QHBoxLayout()
#    h1.addWidget(lineEdit)
#    h1.addWidget(go)
#
#    ok = QPushButton("&OK")
#    cancel = QPushButton("&Cancel")
#
#    h2 = QHBoxLayout()
#    h2.addStretch(1)
#    h2.addWidget(ok)
#    h2.addWidget(cancel)
#
#    layout = QVBoxLayout()
#    layout.addLayout(h1)
#    layout.addLayout(h2)


    widget.setLayout(layout)
    widget.show()

    app.exec_()
    '''
    root = Tk()
    app = Application(root)
    root.geometry('1280x720')
    #root.geometry('640x480')
    root.mainloop()
    #root.destroy()
    '''
