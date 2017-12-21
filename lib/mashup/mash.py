
# -*- coding: utf8 -*-
#!/usr/bin/env python27
import librosa
from pydub import AudioSegment

from ..pre import *

class mash:
    """
    ---member---
        seedSig: raw wave of seed
        seedSr : sample rate of seed
        candSig: raw wave of candidate
        candSr : sample rate of candidate
        resultSig :raw wave of result
        resultSr : sample rate of result
    ---method---
        __init__(seedName, candName):
            pass name as string that represent .pgz file path or
        output(path):
            write out wave to path

    """
    def __init__(self, seedName, candName):
            seg = load(candName)
            self.candSig= seg.signal
            self.candSr = seg.sr
            seg = load(seedName)
            self.seedSig= seg.signal
            self.seedSr = seg.sr
            self.resultSig = np.array([])
            self.resultSr = seg.sr

    def output(self, path):
        self.resultSig = self.candSig
        librosa.output.write_wav(path, self.resultSig, self.resultSr)

    def time_stretch(self, multiplier):
        #self.candSig = librosa.effects.time_stretch(self.candSig,multiplier)
        self.candSig = pyrb.time_stretch(self.candSig, self.candSr, multiplier)

    def pitch_shift(self, n_step):
        #self.candSig = librosa.effects.pitch_shift(self.candSig, self.candSr, n_step)
        self.candSig = pyrb.pitch_shift(self.candSig, self.candSr, n_step)
    
    """
    def fade_in(self,time=1000):
        length = int(self.candSr * time * 0.001)
        for i in xrange(length):
            self.candSig[i] = self.candSig[i] * i / length
        return self

    def fade_out(self,time=1000):
        length = int(self.candSr * time * 0.001)
        sigLength = len(self.candSig)
        for i in xrange(length):
            self.candSig[sigLength-i-1] = self.candSig[sigLength-i-1] * i / length
        return self
    
    def overlay(self,seed_start_time,cand_start_time,cand_end_time=-1):
        if self.candSr * cand_end_time >= len(self.candSig) or cand_end_time == -1 or cand_end_time <= cand_start_time :
            cand_end_frame = len(self.candSig)
        else:
            cand_end_frame = int(self.candSr * cand_end_time * 0.001)
        
        cand_start_frame = int(self.candSr * cand_start_time * 0.001)
        seed_start_frame = int(self.seedSr * seed_start_time * 0.001)
        j=0
        self.resultSig = self.seedSig
        
        for i in xrange(len(self.seedSig)):
            if i >= seed_start_frame and cand_start_frame+j < cand_end_frame :
                self.resultSig[i] = self.seedSig[i]*0.8 + self.candSig[cand_start_frame+j]*0.5
                j+=1
            else:
                self.resultSig[i] = self.seedSig[i]

    """
