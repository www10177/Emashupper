# -*- coding: utf8 -*-

from __future__ import division
import os
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import cPickle
import gzip
import pyrubberband as pyrb


class PreAudio:

    """
    Class to store the characteristic data of wave
    ---member---
    name
    signal, sr
    chroma
    tempo
    spec

    ---Method---
    visualize (mode):
        Visualize the wave ,mode= wave, chromagram or spectrogram
    stretch_seg(frameCount):
        stretch signal to specific frame
    """

    def __init__(self, filePath):
        self.name = os.path.splitext(os.path.basename(filePath))[0]
        self.signal, self.sr = librosa.load(filePath,sr=None)
        self.chroma = librosa.feature.chroma_stft(self.signal, sr=self.sr)
        self.tempo = librosa.beat.beat_track(self.signal, sr=self.sr)[0]
#        self.tempo = librosa.beat.tempo(self.signal)
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
        elif mode == 'all':
            self.visualize('wave')
            self.visualize('chromagram')
            self.visualize('spectrogram')
        else:
            print "ERROR : Mode Error"

    def stretch_seg(self, frameCount):
        # parameter should be tuned
        # decrease or increase multiplier if the frame after adjusted is not
        # equal to frameCount
        approach_para = 0.00001
        # # difference_upbound = 10
        # if difference of two signal frame is bigger than difference_upbound,
        # multiplier would be adjusted
        # # approach_para_mul = 1  # increase the speed of approach

        ori = self.signal
        multiplier = float(self.chroma.shape[1] / frameCount)
        count = 1
        # aprroaching if frame count is not same
        # but it should be useless right now QQ
        while self.chroma.shape[1] != frameCount:
            self.signal = pyrb.time_stretch(ori, self.sr, multiplier)
            self.chroma = librosa.feature.chroma_stft(self.signal)
            difference = self.chroma.shape[1]-frameCount
            if difference < 0:
                # signal after adjusted is too short
                multiplier -= approach_para
            elif difference > 0:
                # signal after adjusted is too long
                multiplier += approach_para
            # print 'count : ', count, ' difference : ', difference,
            # self.chroma.shape[1]
            count += 1
        self.chroma = librosa.feature.chroma_stft(self.signal)
        self.tempo = librosa.beat.tempo(self.signal)
        self.spec = librosa.feature.melspectrogram(self.signal, sr=self.sr)
        print 'adjusted : ', self.name, ' with ', count - 1, ' times aprroaching', ' with multiplier = ', multiplier

    def save(self, savePath):
        with gzip.open(os.path.join(savePath, self.name+'.pgz'), 'wb') as pgz:
            cPickle.dump(self, pgz)
        # print "create ", self.name


