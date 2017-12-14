# -*- coding: UTF-8 -*-  
import librosa
from pandas import read_csv
import os
import numpy as np
from lib import pre


#Paramaeters
PgzLocation= '../pgz/'

#Use this class to color output
class COLOR:# {{{
    END = '\033[0m'  
    RED  = '\033[31m' 
    GREEN  = '\033[32m' 
    ORANGE  = '\033[33m' 
    BLUE  = '\033[34m' 
    PURPLE  = '\033[35m' # }}}

#Read Song List and Choose which song as seed 
csv = read_csv(os.path.join(PgzLocation , 'metadata.csv'))
print COLOR.ORANGE+'{:<3} |  {:<12} '.format('ID','Song Name')+COLOR.END
print '================'

for count, name in enumerate(csv['song name']):
    print '{:<3} | {:<12} '.format(count, name)
id = input("Please Enter ID...")

#Load songs and metadata
seed_seg_count = csv['segmentation count'][id]
seedname = csv['song name'][id]
seed = [None] * seed_seg_count
for i in xrange(0,seed_seg_count):
    name = os.path.join(PgzLocation,seedname+'_'+str(i+1)+'.pgz')
    seed[i] = pre.load(name)
    print 'loaded ',seed[i].name
signal = seed[0].signal
for i in seed:
    print i.name,i.signal.shape
    signal = np.concatenate((signal,i.signal))
