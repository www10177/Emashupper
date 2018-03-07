#!/usr/bin/env/python27
# -*- coding: utf8 -*-
from __future__ import print_function
import msaf
import librosa
from pydub import AudioSegment
import os
from sys import argv

"""
    It's OKAY if the original song file is *.mp3.
"""

songBoundary = {}
def segment(fileLocation, toLocation,songLocation, songToLocation):
    print("Processing instrumental list...")
    for path, dir, files in os.walk(fileLocation):
        for filename in files:
            if filename.endswith(".mp3"):
                sound = AudioSegment.from_mp3(os.path.join(path, filename))
                filename = os.path.splitext(filename)[0]
                filename = filename+".wav"
                sound.export(os.path.join(toLocation, filename), format="wav")

            if not filename.endswith(".wav"):
                print ("Please check your audio file type: " + filename)
                continue

            audio_file = os.path.join(path, filename)
            song = AudioSegment.from_wav(audio_file)
            print ('Segment ' + audio_file)

            # Segment the file using default MSAF parameters
            boundaries, labels = msaf.process(audio_file)
            print(boundaries)
            songBoundary[filename[:filename.rfind('(inst')]] = boundaries
            '''
                Using unit in milliseconds(ten_seconds = 10 * 1000)
                first_10_seconds = song[:ten_seconds]
                last_5_seconds = song[-5000:]
            '''
            segments = list()
            boundaries *= 1000
            buff = 2500
            for index in xrange(1,len(boundaries)):
                if index == 1 or index == len(boundaries)-2 : continue
                elif index == 2 or index == len(boundaries)-1 :
                    segments.append(song[max(0, boundaries[index-2]-buff)
                                         : min(boundaries[len(boundaries)-1], boundaries[index]+buff)])
                else:
                    segments.append(song[boundaries[index-1]-buff:boundaries[index]+buff])

            for index in xrange(len(segments)):
                output = filename[:filename.rfind('.')] + '_' + str(index+1) + filename[filename.rfind('.'):]
                out_format = filename.split('.')[-1]
                segments[index].export(os.path.join(toLocation, output), format = out_format)

    print("Processing vocal list...")
    for path, dir, files in os.walk(songLocation):
        for filename in files:
            if filename.endswith(".mp3"):
                sound = AudioSegment.from_mp3(os.path.join(path, filename))
                filename = os.path.splitext(filename)[0]
                filename = filename+".wav"
                sound.export(os.path.join(songToLocation, filename), format="wav")

            if not filename.endswith(".wav"):
                print ("Please check your audio file type: " + filename)
                continue

            audio_file = os.path.join(path, filename)
            song = AudioSegment.from_wav(audio_file)
            print ('Segment ' + audio_file)

            segments = list()
            if filename.rfind('(vocal') != -1:
                boundaries = songBoundary[filename[:filename.rfind('(vocal')]]
            else:
                boundaries = songBoundary[filename[:filename.rfind('.')]]
            print (boundaries)

            for index in xrange(1,len(boundaries)):
                if index == 1 or index == len(boundaries)-2 : continue
                elif index == 2 or index == len(boundaries)-1 :
                    segments.append(song[max(0, boundaries[index-2]-buff)
                                         : min(boundaries[len(boundaries)-1], boundaries[index]+buff)])
                else:
                    segments.append(song[boundaries[index-1]-buff:boundaries[index]+buff])

            for index in xrange(len(segments)):
                output = filename[:filename.rfind('.')] + '_' + str(index+1) + filename[filename.rfind('.'):]
                out_format = filename.split('.')[-1]
                segments[index].export(os.path.join(songToLocation, output), format = out_format)


if __name__ == "__main__":
    if len(argv) != 5:
        print ("USAGE : python Segmentation.py $INST_FROM $INST_TO $VOCAL_FROM $VOCAL_TO ")
        print (" This small program will convert *.wav/*.mp3 in subfolder of $FROM to *_(1..N).wav and save to $TO")
    else:
        segment(argv[1], argv[2], argv[3], argv[4])

