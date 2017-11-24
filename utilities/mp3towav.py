#!/usr/bin/env/python27
# Module : pydub
# This small program convert music from mp3 to wav


from pydub import AudioSegment
import os
from sys import argv


def converter(fileLocation, toLocation):
    for path, dir, files in os.walk(fileLocation):
        for filename in files:
            if filename.endswith(".mp3"):
                sound = AudioSegment.from_mp3(os.path.join(path, filename))
                filename = os.path.splitext(filename)[0]
                filename = filename+".wav"
                sound.export(os.path.join(toLocation, filename), format="wav")
                print 'converted ' + os.path.join(path,filename)


if __name__ == "__main__":
    if len(argv) != 3:
        print "USAGE : python mp3towav.py $FROM $TO"
        print " This small program will convert *.mp3 in subfolder of $FROM to *.wav and save to $TO"
    else:
        converter(argv[1], argv[2])
