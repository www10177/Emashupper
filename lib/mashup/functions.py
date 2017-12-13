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
    #input_path = "../wav/"
    #input_file = "'Ed Sheeran - Shape Of You (Instrumental)_4.wav'"
    #cmd = FFMPEG_CMD + ' -v ' + input_path + input_file
    cmd = FFMPEG_CMD + ' -v ' + input_file
    #cmd = "ffmpeg-normalize -v ../wav/'Ed Sheeran - Shape Of You (Instrumental)_2.wav'"
    p = subprocess.Popen(shlex.split(cmd))
