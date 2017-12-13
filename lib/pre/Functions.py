# -*- coding: utf8 -*-

import os
import cPickle
import gzip
from .PreAudio import *

__all__=['write','preprocessing','load']

def write(filePath, savePath):
    '''
    create a PreAudio instance from .wav and save in to .pgz
    ---parameter---
    filePath = input .wav file path
    savePath = output .pgz file path
    '''
    f = PreAudio(filePath)
    f.save(savePath)


def preprocessing(inputPath, outputPath):
    '''
    do "write" method on all .wav in "inputPath", which converted all .wav in
    the inputPath, create PreAudio instance and save it in outputPath
    ---parameter---
    inputPath = folder path of all input .wav
    outputPath = folder path to save .pgz file
    '''

    for dirpath, dirs, files in os.walk(inputPath):
        for i, f in enumerate(files):
            if f.endswith('.wav'):
                write(os.path.join(dirpath, f), outputPath)
                print 'processed : '+f
            print 'progress : ', i+1, ' of ', len(files)


def load(filePath):
    '''load pgz file of PreAudio classs, which created by 'write' method'''
    with gzip.open(filePath, 'rb') as pgz:
        f = cPickle.load(pgz)
        return f


