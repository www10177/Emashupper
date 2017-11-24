# -*- coding: utf8 -*-
#!/usr/bin/env python27

import os
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import cPickle
import gzip
from math import sqrt, pow


class PreAudio:

    """
    Class to store the characteristic data of wave
    ---member---
    signal, sr
    chroma
    tempo
    spec

    ---Method---
    visualize (mode):
        Visualize the wave ,mode= wave, chromagram or spectrogram
    """

    def __init__(self, filename):
        self.signal, self.sr = librosa.load(filename)
        self.chroma = librosa.feature.chroma_stft(self.signal)
        self.tempo = librosa.beat.tempo(self.signal)
        self.spec = librosa.feature.melspectrogram(self.signal, sr=self.sr)

    def visualize(self, mode='wave'):
        if mode == 'wave':
            librosa.display.waveplot(self.signal, sr=self.sr)
            plt.title('wave')
            plt.show()
        elif mode == 'chromagram':
            plt.figure(figsize=(10, 4))
            librosa.display.specshow(
                self.chroma, y_axis='chroma', x_axis='time', sr=self.sr)
            plt.colorbar()
            plt.title('chromagram')
            plt.tight_layout()
            plt.show()
        elif mode == 'spectrogram':
            librosa.display.specshow(librosa.power_to_db(self.spec, ref=np.max),
                                     y_axis='mel', fmax=8000,
                                     x_axis='time')
            plt.colorbar(format='%+2.0f dB')
            plt.tight_layout()
            plt.title('spectrogram')
            plt.show()
        elif mode =='all':
            librosa.display.waveplot(self.signal, sr=self.sr)
            plt.title('wave')
            plt.show()
            plt.figure(figsize=(10, 4))
            librosa.display.specshow(
                self.chroma, y_axis='chroma', x_axis='time', sr=self.sr)
            plt.colorbar()
            plt.title('chromagram')
            plt.tight_layout()
            plt.show()
            librosa.display.specshow(librosa.power_to_db(self.spec, ref=np.max),
                                     y_axis='mel', fmax=8000,
                                     x_axis='time')
            plt.colorbar(format='%+2.0f dB')
            plt.tight_layout()
            plt.title('spectrogram')
            plt.show()

        else:
            print "ERROR : Mode Error"


class Mashability:
    '''
    Class to calculate mashability
    ---member---
    seed : seed song data read from pgz file, which is PreAudio Class
    cand : candicate song data read from pgz file, which is PreAudio Class
    ---method---
    __init__(seed, cand):
        seed :an instance of PreAudio class of seed song
        cand :an instance of PreAudio class of cand song
    cosine(self,vec1,vec2):
        return cosine similarity of vec1 and vec2
    chroma():
        return chroma similarity of seed and cand
    rhythm():
        return rhythm similarity of seed and cand
    spectral():
        return spectral similarity of seed and cand
    mash():
        ={'chroma':value, 'rhythm':value, 'spectral':value}
        return the dictionary of all similarity (chroma, rhythm, spectral)
    '''

    def __init__(self, seed, candidate):
        self.seed = seed
        self.cand = candidate

    def cosine(self, vec1, vec2):
        average = 0.0
        product = vec1D = vec2D = 0.0
        for chromaC, chroma in enumerate(vec1):
            product += vec1[chromaC]*vec2[chromaC]
            vec1D += pow(vec1[chromaC], 2)
            vec2D += pow(vec2[chromaC], 2)

        return product / (sqrt(vec1D) * sqrt(vec2D))

    def chroma(self):
        chroma = 0.0
        seedC = self.seed.chroma.transpose()
        candC = self.cand.chroma.transpose()
        if seedC.shape != candC.shape:
            print "the shape of two chromagram is not premitted"
            # raise None
        for i, frame in enumerate(seedC):
            if i >= candC.shape[0]:
                break
            chroma += self.cosine(seedC[i], candC[i])
        return chroma/seedC.shape[0]

    def rhythm(self):
        return 1-(abs(self.seed.tempo[0]-self.cand.tempo[0]
                      ) / self.seed.tempo[0])

    def spectral(self):
        # might be buggy
        seed = self.seed.spec.transpose()
        cand = self.cand.spec.transpose()
        result = np.array([])
        for frameC, frame in enumerate(seed):
            sum = 0
            for sC, spec in enumerate(seed[frameC]):
                sum += seed[frameC][sC] + cand[frameC][sC]
            result = np.append(result, sum / seed[frameC].shape[0])
        s = np.sum(result)
        sumToUnity = np.vectorize(lambda x: x/s)
        result = sumToUnity(result)
        return 1-np.mean(result)

    def mash(self):
        return {
            'chroma': self.chroma(),
            'rhythm': self.rhythm(),
            'spectral': self.spectral()}


def write(filePath, savePath):
    '''
    create a PreAudio instance from .wav and save in to .pgz
    ---parameter---
    filePath = input .wav file path
    savePath = output .pgz file path
    '''
    f = PreAudio(filePath)
    fileName = os.path.splitext(os.path.basename(filePath))[0] + '.pgz'
    with gzip.open(os.path.join(savePath, fileName), 'wb') as pgz:
        cPickle.dump(f, pgz)
    print "create ", fileName


def preprocessing(inputPath, outputPath):
    '''
    do "write" method on all .wav in "inputPath", which converted all .wav in
    the inputPath, create their PreAudio instances and save them to outputPath
    ---parameter---
    inputPath = folder path of all input .wav
    outputPath = folder path to save .pgz file
    '''

    for dirpath, dirs, files in os.walk(inputPath):
        for i, f in enumerate(files):
            if f.endswith('.wav'):
                write(os.path.join(dirpath, f), outputPath)
            print 'progress : ', i+1, ' of ', len(files)


def load(filePath):
    '''load pgz file of PreAudio classs, which created by 'write' method'''
    with gzip.open(filePath, 'rb') as pgz:
        f = cPickle.load(pgz)
        return f


if __name__ == '__main__':
    # f = load('../pgz/田馥甄 - 小幸運 (原版伴奏)_1.pgz')
    # f2 = load('../pgz/田馥甄 - 小幸運 (原版伴奏)_2.pgz')
    f = load('./mix.pgz')
    f.visualize('all')
