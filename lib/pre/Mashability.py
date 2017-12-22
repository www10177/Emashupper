# -*- coding: utf8 -*-

from __future__ import division
import os
import numpy as np
from math import sqrt, pow
from .PreAudio import *
import dtw
from numpy.linalg import norm

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
            if vec1[chromaC] ==0 or vec2[chromaC]==0:
                # to deal with bugs of chromagram = 0
                continue
            product += vec1[chromaC]*vec2[chromaC]
            vec1D += pow(vec1[chromaC], 2)
            vec2D += pow(vec2[chromaC], 2)
        if vec1D == 0 or vec2D ==0 :
            return 0
        return product / (sqrt(vec1D) * sqrt(vec2D))

    def dtw(self,vec1,vec2):
        dist, cost, acc, path = dtw(vec1, vec2, dist=lambda vec1, vec2: norm(vec1 - vec2, ord=1))
        return dist

    def chroma(self):
        chroma = 0.0
        
        seedC = self.seed.chroma.transpose()
        candC = self.cand.chroma.transpose()

        for i, frame in enumerate(seedC):
            if i >= candC.shape[0] :
                break
            # print seedC[i],candC[i]
            chroma += self.cosine(seedC[i], candC[i])

        return chroma/seedC.shape[0]

#        seedC = self.seed.chroma
#        candC = self.cand.chroma
#
#        for i, frame in enumerate(seedC):
#            dist = self.dtw(seedC[i], candC[i])



    def rhythm(self):
        return 1-(abs(self.seed.tempo[0]-self.cand.tempo[0]
                      ) / self.seed.tempo[0])

    def spectral(self):
        # might be buggy
        seed = self.seed.spec.transpose()
        cand = self.cand.spec.transpose()
        result = np.array([])
        # print seed.shape, cand.shape
        for frameC, frame in enumerate(seed):
            sum = 0
            if frameC >= cand.shape[0]:
                # print 'spectal braeak'
                break
            for sC, spec in enumerate(seed[frameC]):
                sum += seed[frameC][sC] + cand[frameC][sC]
            result = np.append(result, sum / seed[frameC].shape[0])
        s = np.sum(result)
        sumToUnity = np.vectorize(lambda x: x/s)
        result = sumToUnity(result)
        return 1-np.mean(result)

    def mash(self,chroma = 0.55, rhythm=0.35, spectral =0.1):
        c=self.chroma()
        r=self.rhythm()
        s=self.spectral()
        return c*chroma+r*rhythm+s*spectral
