# -*- coding: utf8 -*-
#!/usr/bin/env python27
import librosa
from pydub import AudioSegment

from ..pre import *

def volume_adjust(input_file):
    import subprocess
    import shlex
    '''
        Command format: " ffmpeg-normalize -v <input> "
        e.g. "ffmpeg-normalize -v ../wav/'Shape Of You (Instrumental)_2.wav'"
        File will be named by " normalized-<input> "
        e.g. "normalized-Shape Of You (Instrumental)_2.wav"
        '''
    
    FFMPEG_CMD = "ffmpeg-normalize"
    cmd = FFMPEG_CMD + ' -v -f ' + input_file
    p = subprocess.Popen(shlex.split(cmd))
    
def fade_in(sig,sr,time=2500):
    length = int(sr * time * 0.001)
    for i in xrange(length):
        sig[i] = sig[i] * i / length
    
def fade_out(sig,sr,time=2500):
    length = int(sr * time * 0.001)
    sigLength = len(sig)
    for i in xrange(length):
        sig[sigLength-i-1] = sig[sigLength-i-1] * i / length
    
def overlay(candSig,candSr,seedSig,seedSr,seed_start_time=0,cand_start_time=0,cand_end_time = -1):
    ''' Noted that time unit is 'ms'(0.0001 sec.) '''
    if cand_start_time > cand_end_time:
        cand_start_time = 0.0
    elif cand_start_time == cand_end_time:
        return seedSig
    
    if candSr * cand_end_time >= len(candSig) or cand_end_time == -1 or cand_end_time <= cand_start_time :
        cand_end_index = len(candSig)
    else:
        cand_end_index = int(candSr * cand_end_time * 0.001)
        candSig = candSig[:cand_end_index]
    
    #print candSig
    fade_in(candSig,candSr)
    fade_out(candSig,candSr)
    #print candSig
    cand_start_index = int(candSr * cand_start_time * 0.001)
    seed_start_index = int(seedSr * seed_start_time * 0.001)
    j=0
    resultSig = seedSig
    
    for i in xrange(len(seedSig)):
        if i >= seed_start_index and cand_start_index+j < cand_end_index :
            resultSig[i] = seedSig[i]*0.5 + candSig[cand_start_index+j]*0.3
            j+=1
        else:
            resultSig[i] = seedSig[i]

    return resultSig

def bridging(preOrderSig, preOrderSr,postOrderSig, postOrderSr, overlapTime = 2500):
    preLength = len(preOrderSig)
    postLength = len(postOrderSig)
    fade_out(preOrderSig, preOrderSr, overlapTime)
    fade_in(postOrderSig, postOrderSr, overlapTime)
    
    overlapLength = int(preOrderSr * overlapTime * 0.001)
    songLength = preLength - overlapLength + postLength
    resultSig = preOrderSig
    
    for i in xrange(preLength+1):
        if i == preLength :
            postOrderSig = postOrderSig[overlapLength:]
            resultSig = np.concatenate((resultSig,postOrderSig))
            break
        elif i >= preLength - overlapLength :
            resultSig[i] = preOrderSig[i] + postOrderSig[i-preLength+overlapLength]
        else :
            resultSig[i] = preOrderSig[i]

    return resultSig

