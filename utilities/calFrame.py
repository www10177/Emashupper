import sys
import os
from sets import Set
import librosa

def encodingPrint(string):
    # a = '\n'.join(string)
    sys.stdout.write('\n'.join(string))
    print '\n'



if len(sys.argv) != 3:
    print(
        "this small program will calculate the frame all segmented wav file in the source folder,\ncalculate the means and save the result as csvs to the destination.\nUSAGE: python calFrame.py SOURCEFOLDER DESTINATION")
else:
    a = ''
    song_list = []
    # file extension checking and processing file name to song list
    for path, folders, files in os.walk(sys.argv[1]):
        for f in files:
            if f.endswith('.wav'):
                f = f[:-4] # to trim .wav off
                #f = filter(lambda x: not (x.isdigit() or x == '_'), f) # to trim _1, _2, _3... off(number of song seg)_
                f = f[:f.rfind('_')]
                song_list.append(f)
    song_list = list(Set(song_list)) # list of all song (no duplicate)
    song_dict = {s : [0,0] for s in song_list} # dict to count total frames and segs of songs
    encodingPrint('('+str(v[0])+', '+str(v[1])+')\t' + k for k,v in song_dict.iteritems())

    # get frame of each song
    for path, folders, files in os.walk(sys.argv[1]):
        for f in files :
            if not f.endswith('.wav'):
                continue
            fTrim = f[:-4] # to trim .wav off
            #fTrim = filter(lambda x: not (x.isdigit() or x == '_'), fTrim) # to trim _1, _2, _3... off(number of song seg)_
            fTrim = fTrim[:fTrim.rfind('_')]
            if not fTrim in song_dict:
                encodingPrint(f + ' is not in song list')
                continue
            fWave, y = librosa.load(os.path.join(path,f))
            song_dict[fTrim][0] += librosa.stft(fWave).shape[1] # add frame count to dict
            song_dict[fTrim][1] += 1 # add segmentation count

    encodingPrint('('+str(v[0])+', '+str(v[1])+')\t' + k for k,v in song_dict.iteritems())
    # transfer dict to csv
    with open(os.path.join(sys.argv[2],'metadata.csv'),'w') as csv:
        csv.write('song name,avg frame,total frame,segmentation count\n') # write csv title
        for song, data in song_dict.iteritems():
            print data
            csv.write(song+','+str(data[0]/data[1])+','+str(data[0])+','+str(data[1])+'\n')
