# -*- coding: utf8 -*-
#!/usr/bin/env python27
import librosa
from pydub import AudioSegment
import pyrubberband as pyrb
import numpy as np
#from ..pre import *

def volume_adjust(input_file):
    import subprocess
    import shlex
    '''
        Command format: " ffmpeg-normalize -v -f <input> -o <output>"
    '''
    
    FFMPEG_CMD = "ffmpeg-normalize"
    cmd = FFMPEG_CMD + ' -v -f ' + input_file +' -o '+ input_file[:-4]+'(NORMALIZED).wav'
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

def time_stretching(sig, sr, degree):
    return pyrb.time_stretch(sig, sr, degree)

def pitch_shifting(sig, sr, degree):
    return pyrb.pitch_shift(sig, sr, degree)

def beat_matching(candSig, candSr, seedSig, seedSr, vocalSig, vocalSr):
    
    candTempo, candBeats = librosa.beat.beat_track(y=candSig, sr=candSr)
    seedTempo, seedBeats = librosa.beat.beat_track(y=seedSig, sr=seedSr)
    
    candBeatsTime = librosa.frames_to_time(candBeats, sr=candSr)
    seedBeatsTime = librosa.frames_to_time(seedBeats, sr=seedSr)
    candBeatsIndex = np.int_(np.round_(candBeatsTime * candSr))
    seedBeatsIndex = np.int_(np.round_(seedBeatsTime * seedSr))

    # candBeatsDiff = np.zeros(len(candBeats)-1)
    # for i in xrange(len(candBeats)-1):
    #     candBeatsDiff[i] = candBeats[i+1] - candBeats[i]

    # seedBeatsDiff = np.zeros(len(seedBeats)-1)
    # for i in xrange(len(seedBeats)-1):
    #     seedBeatsDiff[i] = seedBeats[i+1] - seedBeats[i]

    resultSig = np.zeros(len(seedSig))
    # stretchedFlag = False
    calculateFlag = 1
    degree = int(round(float(seedTempo) / float(candTempo)))
    # print degree

    if calculateFlag == 1:
        # M1: match tempo
        # only find length of beat1-beat0 and tempo(seed)/tempo(cand)
        
        if degree == 0:
            degree = int(round(float(candTempo) / float(seedTempo)))
            diff = float(seedTempo) / float(candTempo) * float(degree)
        else:
            diff = float(seedTempo) / float(candTempo) / float(degree)
        
        stretchedSig = time_stretching(vocalSig,seedSr,float(diff))
        #stretchedSig *= 0.5

#        out = '../result_stretched.wav'
#        librosa.output.write_wav(out,stretchedSig,seedSr)

        shiftedSig = np.zeros(len(seedSig))

        shift_size = seedBeatsIndex[0] - candBeatsIndex[0]
        #print shift_size

        if shift_size > 0:
            for i in xrange(len(stretchedSig)):
                if i+shift_size >= len(shiftedSig):
                    break
                    shiftedSig[i+shift_size] = stretchedSig[i]

        elif shift_size < 0:
            for i in xrange(len(shiftedSig)):
                if i-shift_size >= len(stretchedSig):
                    break
                shiftedSig[i] = stretchedSig[i-shift_size]
        else:
            shiftedSig = stretchedSig

#        out = '../result_vocal.wav'
#        librosa.output.write_wav(out,shiftedSig,seedSr)

#        fade_in(shiftedSig)
#        fade_out(shiftedSig)

#        out = '../shifted.wav'
#        librosa.output.write_wav(out,shiftedSig,seedSr)


#        for i in xrange(len(seedSig)):
#            if i >= len(shiftedSig):
#                shiftedSig = np.concatenate((shiftedSig, seedSig[i:]*0.5))
#                break
#            else:
#                shiftedSig[i] += seedSig[i]*0.5
#        out = '../../result.wav'
#        librosa.output.write_wav(out,shiftedSig,seedSr)

    else:
        # M2: cand needs to match 'each beat' of seed
        for j in xrange(0,len(seedBeatsIndex)+1,degree):
         #     print j,j/degree
            if j/degree >= len(candBeatsIndex):
				break

            start = len(seedSig)-1 if j == len(seedBeatsIndex) else seedBeatsIndex[j]
            end = -1 if j == 0 else seedBeatsIndex[j-1]-1

            for i in xrange(start,end,-degree):
                index = candBeatsIndex[j/degree]+i-start
                if index < 0 or index >= len(candSig):
                    break
                else:
                    resultSig[i] = vocalSig[index]

            if j/degree == 0:
                continue
            else:
                #print candBeatsIndex[j/degree] - candBeatsIndex[(j/degree)-1],start-end-1
                diff = float( float(candBeatsIndex[j/degree] - candBeatsIndex[(j/degree)-1]) / float(start-end-1) / float(degree) )
                print diff
                sig = time_stretching(resultSig[end+1:start+1],vocalSr,float(diff))

            if stretchedFlag == False:
                stretchedSig = sig
                stretchedFlag = True
            else :
                stretchedSig = np.concatenate((stretchedSig, sig))

		out = '../../resultM2_sound.wav'
        librosa.output.write_wav(out,stretchedSig,seedSr)

#        for i in xrange(len(seedSig)):
#            if i >= len(stretchedSig):
#                stretchedSig = np.concatenate((stretchedSig, seedSig[i:]*0.5))
#                break
#            else:
#                stretchedSig[i] += seedSig[i]*0.5
#
#        shiftedSig = stretchedSig[:len(seedSig)]

#        out = '../../resultM2.wav'
#        librosa.output.write_wav(out,shiftedSig,seedSr)

    
    return shiftedSig


def overlay(candSig, candSr, seedSig, seedSr, vocalSig, vocalSr):
#    ''' Noted that time unit is 'ms'(0.001 sec.) '''
#    if cand_start_time > cand_end_time:
#        cand_start_time = 0.0
#    elif cand_start_time == cand_end_time:
#        return seedSig
#
#    if candSr * cand_end_time >= len(candSig) or cand_end_time == -1 or cand_end_time <= cand_start_time :
#        cand_end_index = len(candSig)
#    else:
#        cand_end_index = int(candSr * cand_end_time * 0.001)
#        candSig = candSig[:cand_end_index]

    resultSig = beat_matching(candSig, candSr, seedSig, seedSr, vocalSig, vocalSr)
    fade_in(resultSig,seedSr)
    fade_out(resultSig,seedSr)
    
#    fade_in(candSig,candSr)
#    fade_out(candSig,candSr)

#    cand_start_index = int(candSr * cand_start_time * 0.001)
#    seed_start_index = int(seedSr * seed_start_time * 0.001)
#    j=0
#    resultSig = seedSig
#
#    for i in xrange(len(seedSig)):
#        if i >= seed_start_index and cand_start_index+j < cand_end_index :
#            resultSig[i] = seedSig[i]*0.5 + candSig[cand_start_index+j]*0.5
#            j+=1
#        else:
#            resultSig[i] = seedSig[i]


    for i in xrange(len(seedSig)):
        if i >= len(resultSig):
            shiftedSig = np.concatenate((resultSig, seedSig[i:]))
            break
        else:
            resultSig[i] = resultSig[i] + seedSig[i]

    return resultSig

def bridging(preOrderSig, preOrderSr,postOrderSig, postOrderSr, overlapTime = 2500):
    fade_out(preOrderSig, preOrderSr, overlapTime)
    fade_in(postOrderSig, postOrderSr, overlapTime)
    
    preLength = len(preOrderSig)
    postLength = len(postOrderSig)
    overlapLength = int(postOrderSr * overlapTime * 0.001)
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

