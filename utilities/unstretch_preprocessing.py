import sys
import os
from sets import Set
import sys
sys.path.insert(0,'..')
import lib.pre
from  pandas import read_csv

def find(dataframe, name):
    for count, sname in enumerate(dataframe['song name']):
        if  sname == name :
            return dataframe['avg frame'][count]


if len(sys.argv) != 3:
    print( 'Usage: python unstretch_preprocessing.py SONGFODLER PGZFOLDER')
else :
    inPath= sys.argv[1]
    outPath = sys.argv[2]
#    csv = read_csv(os.path.join(outPath,'metadata.csv'))
    i =0
    for path,dir,files in os.walk(inPath):
        for f in files:
            if f.endswith('wav'):
                # create preaudio instance
                instance  = lib.pre.PreAudio(os.path.join(path,f))
                instance.save(outPath)
            print 'progress : ', i+1, ' of ', len(files)
            i +=1
