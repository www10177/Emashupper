# -*- coding: utf8 -*-
#!/usr/bin/env/python27
from __future__ import print_function
import msaf
import librosa
from pydub import AudioSegment
#import os

# Choose an audio file
audio_file = "./Demo_songs/Chloe Riley - S.T.F.U.(instrumental).mp3"

# Check which type the input audio file is
if audio_file.endswith(".mp3"):
    song = AudioSegment.from_mp3(audio_file)
elif audio_file.endswith("wav"):
    song = AudioSegment.from_wav(audio_file)
else:
    print ("Please change your audio file.")

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
    file_name = audio_file.split('/')[-1]
    output = file_name[:file_name.rfind('.')] + "_" + str(index+1) + file_name[file_name.rfind('.'):]
    out_format = file_name.split('.')[-1]
    segments[index].export("OUTPUT_50/" + output, format = out_format)

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
