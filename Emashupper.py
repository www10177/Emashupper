# -*- coding:utf-8 -*-
from sys import platform as sys_pf
if sys_pf == 'darwin':
    import matplotlib
    matplotlib.use("Qt4Agg")

from Tkinter import *
from lib import pre, mashup
from pandas import read_csv
import os
from subprocess import call,Popen
import numpy as np
import pygame
import matplotlib.pyplot as plt
import librosa.display

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

#Please Modify This Parameter Only#
DataLocationA='../db'
##########

SongPgzLocation = os.path.join(DataLocationA,'pgz/')
PgzLocation= os.path.join(DataLocationA,'pgz/')
WavLocation= os.path.join(DataLocationA,'song/')

from random import randint
from PyQt4 import QtGui
from PyQt4 import QtCore

pygame.mixer.init()
pygame.mixer.set_num_channels(2)

LoadMode = 1
# 0 would load pgz seperately, which might be slower but use less memory
# 1 would load all pgz at once, which might be faster but use more memory

def pathJoin(path,fileName):
    a = path
    if a.endswith('/'):
        b = a + fileName
    else :
        b = a + '/' + fileName
    return b

def nameJoin(path,fileName):
    a = path
    b = fileName
    a = "".join(str(a).split(' '))
    b = "".join(str(b).split(' '))
    return a+b

class Figure_Canvas(FigureCanvas):
    
    def __init__(self, parent=None, width=11, height=5, dpi=100):
        fig = Figure(figsize=(width, height), dpi=100)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
    
        self.axes = fig.add_subplot(111)
    
    def draw(self,x,y,title):
        self.axes.clear()
        self.axes.set_title(title)
        self.axes.plot(x[0],y)

class Window(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.parent = parent
        self.initVar()
        self.initUI()

    def initVar(self):
        # initialize public variable
        self.csv = ''
        self.cateIndex = -1
        self.cateName = ''
        self.seedIndex = -1
        self.seedSegCount = -1
        self.seedName = ''
        self.seed = [None] * self.seedSegCount #PreAudio list of seed song
        self.mashup = [None] * self.seedSegCount #PreAudio list of selected candidated song
        self.mashuppedSig = None

    def initUI(self):
        #initialize UI
        self.setGeometry(150, 30, 830, 540)
        self.setWindowTitle('Emashupper')
        
        palette1 = QtGui.QPalette()
        palette1.setColor(self.backgroundRole(), QtGui.QColor(192,253,123))
        palette1.setBrush(self.backgroundRole(), QtGui.QBrush(QtGui.QPixmap('./material/bg.jpg').scaledToHeight(540)))
        self.setPalette(palette1)
        self.setAutoFillBackground(True)
        self.listbox()
        self.actionElements()
#        self.graphicview = QtGui.QGraphicsView()
#        self.graphicview.setObjectName("graphicview")

    def listbox(self):
        # show all category list
        self.cateListWidget = QtGui.QListWidget(self)
        self.catelist = []

        s=filter(lambda x: os.path.isdir(os.path.join(WavLocation, x)), os.listdir(WavLocation)) 
        for cate in s:
            self.cateListWidget.addItem(cate)
            self.catelist.append(cate)
        self.cateListWidget.setAutoFillBackground(True)
        self.cateListWidget.setStyleSheet('''
            color: white;
            background-image: url('./material/Starry_sky.png');
            ''')
        self.cateListWidget.setFont(QtGui.QFont("Courier",15))
        self.cateListWidget.itemSelectionChanged.connect(self.onselect)
        #set header
        self.cateListWidget.move(30, 90)
        self.cateListWidget.resize(225, 245)
        self.cateListWidget.show()

    def onselect(self):
        # event helper for listbox slection
        # Note here that Tkinter passes an event object to onselect()
        if not self.cateListWidget.selectedItems():
            print ("Please select a category first.")
        else:
            index = self.cateListWidget.currentRow()
            value = self.cateListWidget.currentItem().text()
            self.cateIndex = index
            self.cateName = str(value)
            print 'selected %d: "%s"' % (index, value)
  
    def actionElements(self):
        # initialze buttons,labels...
        seed_generate = QtGui.QPushButton("Generate Random Seed -> ")
        seed_generate.setFont(QtGui.QFont("Courier",15))
        seed_generate.setStyleSheet('''
            background-image: url('./material/button.png');
            background-color: rgba(255, 255, 255, 0);
            ''')
        seed_generate.clicked.connect(self.seedGenerate)

        self.seedNameShow = QtGui.QLabel("\nSeed: ")
        self.seedNameShow.setFont(QtGui.QFont("Courier",15))
        
        self.progressBar = QtGui.QLabel("\n")
        self.progressBar.setFont(QtGui.QFont("Courier",15))

        load_file = QtGui.QPushButton("Load Seed Song Segments ")
        load_file.setFont(QtGui.QFont("Courier",15))
        load_file.setStyleSheet('''
            background-image: url('./material/button.png');
            background-color: rgba(255, 255, 255, 0);
            ''')
        load_file.clicked.connect(self.load)
        
        play_seed = QtGui.QPushButton("Play Seed Song")
        play_seed.setFont(QtGui.QFont("Courier",15))
        play_seed.setStyleSheet('''
            background-image: url('./material/button.png');
            background-color: rgba(255, 255, 255, 0);
            ''')
        play_seed.clicked.connect(self.playSeed)
        
        stop_seed = QtGui.QPushButton("Stop Playing Seed")
        stop_seed.setFont(QtGui.QFont("Courier",15))
        stop_seed.setStyleSheet('''
            background-image: url('./material/button.png');
            background-color: rgba(255, 255, 255, 0);
            ''')
        stop_seed.clicked.connect(self.stopPlaySeed)
        
        show_seed = QtGui.QPushButton("Show Seed Wave")
        show_seed.setFont(QtGui.QFont("Courier",15))
        show_seed.setStyleSheet('''
            background-image: url('./material/button.png');
            background-color: rgba(255, 255, 255, 0);
            ''')
        show_seed.clicked.connect(self.seedShow)
        
        do_mash = QtGui.QPushButton("Mashup")
        do_mash.setFont(QtGui.QFont("Courier",15))
        do_mash.setStyleSheet('''
            background-image: url('./material/button.png');
            background-color: rgba(255, 255, 255, 0);
            ''')
        do_mash.clicked.connect(self.mashupSong)
        
        play_mash = QtGui.QPushButton("Play Mashupped Song")
        play_mash.setFont(QtGui.QFont("Courier",15))
        play_mash.setStyleSheet('''
            background-image: url('./material/button.png');
            background-color: rgba(255, 255, 255, 0);
            ''')
        play_mash.clicked.connect(self.playMashuped)
        
        stop_mash = QtGui.QPushButton("Stop Playing")
        stop_mash.setFont(QtGui.QFont("Courier",15))
        stop_mash.setStyleSheet('''
            background-image: url('./material/button.png');
            background-color: rgba(255, 255, 255, 0);
            ''')
        stop_mash.clicked.connect(self.stopPlayMashuped)
        
        show_mash = QtGui.QPushButton("Show Mashupped Song Wave")
        show_mash.setFont(QtGui.QFont("Courier",15))
        show_mash.setStyleSheet('''
            background-image: url('./material/button.png');
            background-color: rgba(255, 255, 255, 0);
            ''')
        show_mash.clicked.connect(self.showMashuped)
        
        layout0 = QtGui.QVBoxLayout()
        layout0.addWidget(seed_generate)
        layout0.setAlignment(QtCore.Qt.AlignTop)

        emp = QtGui.QLabel("")
        layout2 = QtGui.QVBoxLayout()
        layout2.setAlignment(QtCore.Qt.AlignTop)
        layout2.addWidget(self.seedNameShow)
        layout2.addWidget(emp)
        layout2.addWidget(emp)
        layout2.addWidget(load_file)
        layout2.addWidget(emp)
        layout2.addWidget(play_seed)
        layout2.addWidget(emp)
        layout2.addWidget(stop_seed)
        layout2.addWidget(emp)
        layout2.addWidget(show_seed)

        layout3 = QtGui.QVBoxLayout()
        layout3.setAlignment(QtCore.Qt.AlignTop)
        layout3.addWidget(self.progressBar)
        layout3.addWidget(emp)
        layout3.addWidget(emp)
        layout3.addWidget(do_mash)
        layout3.addWidget(emp)
        layout3.addWidget(play_mash)
        layout3.addWidget(emp)
        layout3.addWidget(stop_mash)
        layout3.addWidget(emp)
        layout3.addWidget(show_mash)

        layout = QtGui.QHBoxLayout()
        layout.addLayout(layout0)
        layout.addStretch()
        layout.addLayout(layout2)
        layout.addStretch()
        layout.addLayout(layout3)
        self.setLayout(layout)
    
    def load(self):
        c = self.csv # To simpilfy 
        self.seedIndex = c.index[c['song name'] == self.seedName].tolist()[0]
        self.seedSegCount= self.csv['segmentation count'][self.seedIndex]
        print self.seedIndex
        print self.seedName
        self.seed = [None] * self.seedSegCount
        for i in xrange(0,self.seedSegCount):
            name = pathJoin(PgzLocation+self.cateName+'/inst/',self.seedName+'(inst)'+'_'+str(i+1)+'.pgz')
            self.seed[i] = pre.load(name)
            print 'loaded ',self.seed[i].name
        self.progressBar.setText("\nDone Loading Segments.")

    def seedGenerate(self):
        #open the songlist(csv) of the chosen category, and show the ramdomly choice
        self.csv = read_csv(PgzLocation+self.cateName+'/metadata.csv')
#        print self.cateName
        songs = [s.rstrip('\n') for s in self.csv['song name']]
        self.seedName = songs[randint(1,len(songs)-1)]

        seedLabel = self.seedName[:18]
        last = self.seedName[18:]
        while len(last) >= 24:
            seedLabel = seedLabel + '\n' + last[:24]
            last = last[24:]
        seedLabel = seedLabel + '\n' + last
        self.seedNameShow.setText("\nSeed: "+seedLabel)
    
    def seedShow(self):
        signal = self.seed[0].signal
        for i in self.seed[1:]:
            signal = np.concatenate((signal,i.signal))
        
        # dr = Figure_Canvas()
        # dr.draw([[i for i in xrange(len(signal))],self.seed[0].sr], signal,'Seed Song Waveplot')
        # graphicscene = QtGui.QGraphicsScene()
        # graphicscene.addWidget(dr)
        # self.graphicview.setScene(graphicscene)
        # self.graphicview.setWindowTitle('Seed Song Waveplot')
        # self.graphicview.show()

        librosa.display.waveplot(signal, sr=self.seed[0].sr)
        plt.title('Seed Song Waveplot')
        plt.show()



    def playSeed(self):
        seedsound = pygame.mixer.Sound(os.path.join(WavLocation+self.cateName+'/inst/',self.seedName+'(inst)'+ '_1.wav'))
        if not pygame.mixer.Channel(1).get_busy():
            pygame.mixer.Channel(1).play(seedsound)
#        if sys.platform == 'darwin':
#            Popen(["afplay",os.path.join(WavLocation+self.cateName+'/inst/',self.seedName+'(inst)'+ '_1.wav')])

    def stopPlaySeed(self):
        pygame.mixer.Channel(1).stop()

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
                candSegPath = pathJoin(PgzLocation+self.cateName+'/inst/',candName+'(inst)'+'_'+str(candSegIndex)+'.pgz')
                seg.append(pre.load(candSegPath))
        print "loaded all segments"

        #Mashupping
        for seedSegNow in xrange(0,self.seedSegCount):
            # iterate all segmentations in seed song
            maxMashability = -1000
            maxSeg = None
            maxIndex = -1
            for segIndex ,cand in enumerate(seg):
                # iterate all segmentation
                masha = pre.Mashability(self.seed[seedSegNow], cand).mash()
                if maxMashability < masha:
                    maxMashability = masha
                    maxSeg = cand
                    maxIndex = segIndex
                if segIndex % 10  == 0:
                    print 'compared : ',segIndex, ' of ' ,len(seg)
            print 'maxSeg = ',maxSeg.name
            mashabilityList[seedSegNow] = maxMashability

            vocalSegPath = pathJoin(SongPgzLocation+self.cateName+'/vocal/',maxSeg.name[:maxSeg.name.rfind('(inst')] + '(vocal)' + maxSeg.name[maxSeg.name.rfind('_'):]+'.pgz')

            print 'Mashed File: '+ maxSeg.name[:maxSeg.name.rfind('(inst')] + '(vocal)' + maxSeg.name[maxSeg.name.rfind('_'):]+'.wav'
            
            if maxMashability >= threshold :
                self.mashup[seedSegNow] = pre.load(vocalSegPath)
            else:
                print('Mashability = '+str(maxMashability)+' < Threshold , Skip ...')

            print "Mashed : #"+str(seedSegNow+1)+" of "+str(self.seedSegCount)

            del seg[maxIndex]

        print 'selected : '
        for index, candSeg in enumerate(self.mashup):
            if candSeg :
                print candSeg.name,' : ', mashabilityList[index]

        seg = [None] * self.seedSegCount

        for i in xrange(self.seedSegCount):
            # overlay cand and seed
            if self.mashup[i] :
                instSegPath = pathJoin(WavLocation+self.cateName+'/inst/',maxSeg.name + '.wav')
                instSig, instSr = librosa.load(instSegPath,sr = None)
                seg[i] = mashup.overlay(instSig, instSr, self.seed[i].signal,self.seed[i].sr, self.mashup[i].signal, self.mashup[i].sr)

            else :
                seg[i] = self.seed[i].signal
    
            # bridging
            if i == 0 :
                signal = seg[i]
            else:
                signal = mashup.bridging(signal, self.seed[0].sr,seg[i], self.seed[0].sr,5000)
                    
        self.mashuppedSig = signal
        self.saveMashuped()
        self.progressBar.setText("\nMashupped Song\nhas been saved.")
    
    
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
                    candSegPath = pathJoin(PgzLocation+self.cateName+'/inst/',candName+'_'+str(candSegIndex)+'.pgz')
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
    
        vocalSegPath = pathJoin(SongPgzLocation+self.cateName+'/vocal/',maxSeg.name[:maxSeg.name.rfind('(inst')] + '(vocal)' + maxSeg.name[maxSeg.name.rfind('_'):]+'.pgz')
        
        if maxMashability >= threshold :
            self.mashup[seedSegNow] = pre.load(vocalSegPath)
        else: print('Mashability = ' + maxMashability + ' < Threshold , Skip...')
            
        mashupedDic.add({maxSeg.name:True})

        print 'selected : '
        for index, candSeg in enumerate(self.mashup):
            print candSeg.name,' : ', mashabilityList[index]


        seg = [None] * self.seedSegCount
        for i in xrange(self.seedSegCount):
            # overlay cand and seed
            if self.mashup[i] :
                instSegPath = pathJoin(cateLocation+self.cateName+WavLocation,maxSeg.name + '.wav')
                instSig, instSr = librosa.load(instSegPath,sr = None)
                seg[i] = mashup.overlay(instSig, instSr, self.seed[i].signal,self.seed[i].sr, self.mashup[i].signal, self.mashup[i].sr)
            else :
                seg[i] = self.seed[i].signal
            
            # bridging
            if i == 0 :
                signal = seg[i]
            else:
                signal = mashup.bridging(signal, self.seed[0].sr,seg[i], self.seed[0].sr,5000)

        self.mashuppedSig = signal
        self.saveMashuped()
    
    def mashupSong(self):
        if LoadMode == 0:
            print 'Load canidate seperately'
            self.mashupLoadSeperately()
        elif LoadMode == 1:
            print 'Load canidate at once'
            self.mashupLoadAtOnce()

    def saveMashuped(self):
        outputFile = str(nameJoin(str(nameJoin('./',self.seedName)),'_mashupped.wav'))
        librosa.output.write_wav(outputFile,self.mashuppedSig,self.seed[0].sr)
        mashup.volume_adjust(outputFile)
        print ('\nDone processing mashupped song.')

    def playMashuped(self):
        mashsound = pygame.mixer.Sound(str(nameJoin(self.seedName,'_mashupped(NORMALIZED).wav')))
        if not pygame.mixer.Channel(0).get_busy():
            pygame.mixer.Channel(0).play(mashsound)
#        if sys.platform == 'darwin':
#            Popen(["afplay",str(nameJoin(self.seedName,'_mashupped(NORMALIZED).wav'))])

    def stopPlayMashuped(self):
        pygame.mixer.Channel(0).stop()
                                    
    def showMashuped(self):
        if len(self.mashuppedSig) >= 1 :
            # dr = Figure_Canvas()
            # dr.draw([[i for i in xrange(len(self.mashuppedSig))],self.seed[0].sr], self.mashuppedSig,'Mashupped Song Waveplot')
            # graphicscene = QtGui.QGraphicsScene()
            # graphicscene.addWidget(dr)
            # self.graphicview.setScene(graphicscene)
            # self.graphicview.setWindowTitle('Mashupped Song Waveplot')
            # self.graphicview.show()
            librosa.display.waveplot(self.mashuppedSig, sr=self.seed[0].sr)
            plt.title('Mashupped Song Waveplot')
            plt.show()

####################################################################

if __name__ == '__main__':

    print 'Data : ',DataLocationA
    print 'pgz(inst) : ', PgzLocation
    print 'pgz(vocal) : ', SongPgzLocation
    print 'wav : ', WavLocation

    app = QtGui.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())

    
