# -*- coding: utf8 -*-

from __future__ import division
import os
#from lib import pre
from sys import argv

import os
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import cPickle
import gzip


class PreAudio:
    
    """
        Class to store the characteristic data of wave
        ---member---
        name
        signal, sr
        chroma
        tempo
        spec
    """
    
    def __init__(self, filePath):
        self.name = os.path.splitext(os.path.basename(filePath))[0]
        self.signal, self.sr = librosa.load(filePath,sr=None)
        self.chroma = librosa.feature.chroma_stft(self.signal)
        self.tempo = librosa.beat.tempo(self.signal)
        self.spec = librosa.feature.melspectrogram(self.signal, sr=self.sr)
    
    def save(self, savePath):
        with gzip.open(os.path.join(savePath, self.name+'.pgz'), 'wb') as pgz:
            cPickle.dump(self, pgz)
        # print "create ", self.name

def write(filePath, savePath):
    '''
        create a PreAudio instance from .wav and save in to .pgz
        ---parameter---
        filePath = input .wav file path
        savePath = output .pgz file path
    '''
    f = PreAudio(filePath)
    f.save(savePath)

def pgzConverter(fileLocation, toLocation):
    for path, dir, files in os.walk(fileLocation):
        for filename in files:
            if filename.endswith(".wav"):
                # change wav to pgz
                #filename = os.path.splitext(filename)[0]
                write(os.path.join(path,filename),toLocation)
                print 'converted ' + os.path.join(path,filename)
            else:
                print "Please convert "+ filename +" song type to .wav first."


if __name__ == "__main__":
    if len(argv) != 3:
        print "USAGE : python pgzGenerator.py $FROM $TO"
        print " This small program will convert *.wav in subfolder of $FROM to *.pgz and save to $TO"
    else:
        pgzConverter(argv[1], argv[2])
