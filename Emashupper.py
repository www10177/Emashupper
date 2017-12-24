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


SongPgzLocation = '../pgz/vocal/'
PgzLocation = '../pgz/inst/'
WavLocation = '../wav_seg/inst/'
csvLovation = PgzLocation+'metadata.csv'

#from PyQt4.QtGui import *
from PyQt4 import QtGui

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
        # 调用figure下面的add_subplot方法，类似于matplotlib.pyplot下面的subplot方法
        #            # create an axis
        #            ax = self.figure.add_subplot(111)
        #            # discards the old graph
        #            ax.clear()
        #            # plot data
        #            ax.plot(signal, '*-')
        #            # refresh canvas
        #            self.canvas.draw()
    def draw(self,x,y,title):
        self.axes.clear()
#        self.axes.set_xlabel('sec222.')
#        self.axes.set_ylabel('sec.')
        self.axes.set_title(title)
#        time = [float(i / x[1]) for i in x[0]]
        #seq = [str(int(i/60))+':'+str(int(i%60)) for i in time]
#        time = [str(i/x[1]/60)+':'+str((i/x[1])%60) for i in x[0]]
        self.axes.plot(x[0],y)

class Window(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.parent = parent
        self.initVar()
        self.initUI()

    def initVar(self):
        # initialize public variable
        self.csv = read_csv(csvLovation)
        self.seedIndex= -1
        self.seedSegCount=-1
        self.seedName = ''
        self.seed = [None] * self.seedSegCount #PreAudio list of seed song
        self.mashup = [None] * self.seedSegCount #PreAudio list of selected candidated song
        self.mashuppedSig = None
    
#        # a figure instance to plot on
#        self.figure = Figure()
#
#        # this is the Canvas Widget that displays the `figure`
#        # it takes the `figure` instance as a parameter to __init__
#        self.canvas = FigureCanvas(self.figure)
#
#        # this is the Navigation widget
#        # it takes the Canvas widget and a parent
#        self.toolbar = NavigationToolbar(self.canvas, self)

    def initUI(self):
        #initialize UI
        self.setGeometry(150, 30, 960, 540)
        self.setWindowTitle('Emashupper')
        
        palette1 = QtGui.QPalette()
        palette1.setColor(self.backgroundRole(), QtGui.QColor(192,253,123))
        palette1.setBrush(self.backgroundRole(), QtGui.QBrush(QtGui.QPixmap('./material/bg.jpg').scaledToHeight(540)))
        self.setPalette(palette1)
        self.setAutoFillBackground(True)
    
        self.listbox()
        self.actionElements()
        
        self.graphicview = QtGui.QGraphicsView()  # 第一步，创建一个QGraphicsView
        self.graphicview.setObjectName("graphicview")


    def listbox(self):
        # show all song list
        self.songListWidget = QtGui.QListWidget(self)
        self.songlist = []
        for song in self.csv['song name']:
            self.songListWidget.addItem(song)
            self.songlist.append(song)
        
        self.songListWidget.setAutoFillBackground(True)
        self.songListWidget.setStyleSheet('''
            color: white;
            background-image: url('./material/Starry_sky.png');
            ''')
        self.songListWidget.setFont(QtGui.QFont("Courier",15))

        self.songListWidget.itemSelectionChanged.connect(self.onselect)
        #set header!
        self.songListWidget.move(40, 90)
        self.songListWidget.resize(620, 230)
        self.songListWidget.show()

    def onselect(self):
        # event helper for listbox slection
        # Note here that Tkinter passes an event object to onselect()
        if not self.songListWidget.selectedItems():
            print ("Please select a seed song.")
        else:
            index = self.songListWidget.currentRow()
            value = self.songListWidget.currentItem().text()
            self.seedIndex = index
            self.seedName = value
            print 'selected %d: "%s"' % (index, value)

    def actionElements(self):
        # initialze buttons,labels...
        
        load_file = QtGui.QPushButton("-> Load Segments")
        load_file.setFont(QtGui.QFont("Courier",15))
        load_file.setStyleSheet('''
            background-image: url('./material/button.png');
            background-color: rgba(255, 255, 255, 0);
            ''')
        load_file.clicked.connect(self.load)
        
        #seedl = QtGui.QLabel("--- Seed ---")
        play_seed = QtGui.QPushButton("Play Seed Song")
        play_seed.setFont(QtGui.QFont("Courier",15))
        play_seed.setStyleSheet('''
            background-image: url('./material/button.png');
            background-color: rgba(255, 255, 255, 0);
            ''')
        play_seed.clicked.connect(self.playSeed)
        show_seed = QtGui.QPushButton("Show Seed Wave")
        show_seed.setFont(QtGui.QFont("Courier",15))
        show_seed.setStyleSheet('''
            background-image: url('./material/button.png');
            background-color: rgba(255, 255, 255, 0);
            ''')
        show_seed.clicked.connect(self.seedShow)
        
        #mashl = QtGui.QLabel("--- Mashup ---")
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
        
        show_mash = QtGui.QPushButton("Show Mashupped Song Wave")
        show_mash.setFont(QtGui.QFont("Courier",15))
        show_mash.setStyleSheet('''
            background-image: url('./material/button.png');
            background-color: rgba(255, 255, 255, 0);
            ''')
        show_mash.clicked.connect(self.showMashuped)
        
        save_mash = QtGui.QPushButton("Save Mashupped Song")
        save_mash.setFont(QtGui.QFont("Courier",15))
        save_mash.setStyleSheet('''
            background-image: url('./material/button.png');
            background-color: rgba(255, 255, 255, 0);
            ''')
        save_mash.clicked.connect(self.saveMashuped)
        
        #layout = QHBoxLayout()
        layout = QtGui.QVBoxLayout()
        layout.addWidget(load_file)
#        layout.addWidget(seedl)
        layout.addWidget(play_seed)
        layout.addWidget(show_seed)
#        layout.addWidget(mashl)
        layout.addWidget(do_mash)
        layout.addWidget(play_mash)
        layout.addWidget(show_mash)
        layout.addWidget(save_mash)
        
        layout2 = QtGui.QHBoxLayout()
#        layout2.addWidget(self.toolbar)
#        layout2.addWidget(self.canvas)
        layout2.addStretch()
        layout2.addLayout(layout)
        self.setLayout(layout2)
    

    def load(self):
        self.seedSegCount= self.csv['segmentation count'][self.seedIndex]
        self.seed = [None] * self.seedSegCount
        for i in xrange(0,self.seedSegCount):
            name = pathJoin(PgzLocation,'normalized-'+self.seedName+'(inst)'+'_'+str(i+1)+'.pgz')
            self.seed[i] = pre.load(name)
            print 'loaded ',self.seed[i].name

    def seedShow(self):
        signal = self.seed[0].signal
        for i in self.seed[1:]:
            signal = np.concatenate((signal,i.signal))

#            # create an axis
#            ax = self.figure.add_subplot(111)
#            # discards the old graph
#            ax.clear()
#            # plot data
#            ax.plot(signal, '*-')
#            # refresh canvas
#            self.canvas.draw()

        dr = Figure_Canvas()
        dr.draw([[i for i in xrange(len(signal))],self.seed[0].sr], signal,'Seed Song Waveplot')
        graphicscene = QtGui.QGraphicsScene()
        graphicscene.addWidget(dr)
        self.graphicview.setScene(graphicscene)
        self.graphicview.setWindowTitle('Seed Song Waveplot')
        self.graphicview.show()
    

#        librosa.display.waveplot(signal, sr=self.seed[0].sr)
#        plt.title('Seed Wave')
#        plt.show()

    def playSeed(self):
        if sys.platform == 'darwin':
            Popen(["afplay",pathJoin(WavLocation,'normalized-'+self.seedName+'(inst)'+ '_1.wav')])


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
                candSegPath = pathJoin(PgzLocation,'normalized-'+candName+'(inst)'+'_'+str(candSegIndex)+'.pgz')
                seg.append(pre.load(candSegPath))
        print "loaded all seg"

        #Mashupping
        for seedSegNow in xrange(0,self.seedSegCount):
            # iterate all segmentations in seed song

#            # Notice: The first section and the last section will not be mashupped.
#            if seedSegNow == 0 or seedSegNow == self.seedSegCount-1 :
#                continue


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

            vocalSegPath = pathJoin(SongPgzLocation,maxSeg.name[:maxSeg.name.rfind('(inst')] + '(vocal)' + maxSeg.name[maxSeg.name.rfind('_'):]+'.pgz')

            print 'Mashed File: '+ maxSeg.name[:maxSeg.name.rfind('(inst')] + '(vocal)' + maxSeg.name[maxSeg.name.rfind('_'):]+'.wav'

            if maxMashability >= threshold :
                self.mashup[seedSegNow] = pre.load(vocalSegPath)

            else: print('Mashability', maxMashability ,'< Threshold , Skip ...')

            print 'Mashed : #',seedSegNow+1 ,' of ', self.seedSegCount

            del seg[maxIndex]

        print 'selected : '
        for index, candSeg in enumerate(self.mashup):
            if candSeg :
                print candSeg.name,' : ', mashabilityList[index]

        seg = [None] * self.seedSegCount

        for i in xrange(self.seedSegCount):
            # overlay cand and seed
            if self.mashup[i] :
                instSegPath = pathJoin(WavLocation,maxSeg.name + '.wav')
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
                    candSegPath = pathJoin(PgzLocation,candName+'_'+str(candSegIndex)+'.pgz')
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
    
        vocalSegPath = pathJoin(SongPgzLocation,maxSeg.name[:maxSeg.name.rfind('(inst')] + '(vocal)' + maxSeg.name[maxSeg.name.rfind('_'):]+'.pgz')
        
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
                instSegPath = pathJoin(WavLocation,maxSeg.name + '.wav')
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
        print ('Done processing mashupped song.')
    
    def playMashuped(self):
        self.saveMashuped()
        if sys.platform == 'darwin':
            Popen(["afplay",str(nameJoin(str(nameJoin('./normalized-',self.seedName)),'_mashupped.wav'))])

    def showMashuped(self):
        if len(self.mashuppedSig) >= 1 :
            dr = Figure_Canvas()
            dr.draw([[i for i in xrange(len(self.mashuppedSig))],self.seed[0].sr], self.mashuppedSig,'Mashupped Song Waveplot')
            graphicscene = QtGui.QGraphicsScene()
            graphicscene.addWidget(dr)
            self.graphicview.setScene(graphicscene)
            self.graphicview.setWindowTitle('Mashupped Song Waveplot')
            self.graphicview.show()
#            librosa.display.waveplot(self.mashuppedSig, sr=self.seed[0].sr)
#            plt.title('Mashupped Wave')
#            plt.show()

####################################################################

if __name__ == '__main__':
    print 'pgz(inst) : ', PgzLocation
    print 'pgz(song) : ', SongPgzLocation
    print 'wav : ', WavLocation
    
    app = QtGui.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())

    
