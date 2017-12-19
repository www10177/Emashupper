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

def segment(fileLocation, toLocation):
    for path, dir, files in os.walk(fileLocation):
        for filename in files:
            if filename.endswith(".mp3"):
                sound = AudioSegment.from_mp3(os.path.join(path, filename))
                filename = os.path.splitext(filename)[0]
                filename = filename+".wav"
                sound.export(os.path.join(toLocation, filename), format="wav")
            
            if not filename.endswith(".wav"):
                print ("Please check your audio file type.")
                return -1

            audio_file = os.path.join(path, filename)
            song = AudioSegment.from_wav(audio_file)
            print ('Segment ' + audio_file)

            # Segment the file using the default MSAF parameters
            boundaries, labels = msaf.process(audio_file)
            print(boundaries)

            '''
                pydub does things in milliseconds(ten_seconds = 10 * 1000)
                first_10_seconds = song[:ten_seconds]
                last_5_seconds = song[-5000:]
            '''
            segments = list()
            boundaries *= 1000
            buff = 50
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

            '''
            # Sonify boundaries
            sonified_file = audio_file.split('/')[-1].split('.')[-2]+"_sonified.wav"
            sr = 44100
            boundaries, labels = msaf.process(audio_file, sonify_bounds=True,
                                              out_bounds=sonified_file, out_sr=sr)

            # Listen to results
            audio = librosa.load(sonified_file, sr=sr)[0]
            IPython.display.Audio(audio, rate=sr)
            '''


if __name__ == "__main__":
    if len(argv) != 3:
        print ("USAGE : python Segmentation.py $FROM $TO")
        print (" This small program will convert *.wav/*.mp3 in subfolder of $FROM to *_(1..N).wav and save to $TO")
    else:
        segment(argv[1], argv[2])

