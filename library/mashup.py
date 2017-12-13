# -*- coding: utf8 -*-
#!/usr/bin/env python27
import librosa
from pydub import AudioSegment

from pre import *

class mash:
    """
    ---member---
        seedSig: raw wave of seed
        seedSr : sample rate of seed
        candSig: raw wave of candidate
        candSr : sample rate of candidate
        resultSig :raw wave of result
        resultSr : sample rate of result
    ---method---
        __init__(seedName, candName):
            pass name as string that represent .pgz file path or
        output(path):
            write out wave to path

    """
    def __init__(self, seedName, candName):
            seg = load(candName)
            self.candSig= seg.signal
            self.candSr = seg.sr
            seg = load(seedName)
            self.seedSig= seg.signal
            self.seedSr = seg.sr
            self.resultSig = np.array([])
            self.resultSr = seg.sr

    def output(self, path):
        self.resultSig = self.candSig
        librosa.output.write_wav(path, self.resultSig, self.resultSr)

    def time_stretch(self, multiplier):
        self.candSig = librosa.effects.time_stretch(self.candSig,multiplier)

    def pitch_shift(self, n_step):
        self.candSig = librosa.effects.pitch_shift(self.candSig, self.candSr, n_step)

    def bridging(self,fade_in_time=300,fade_out_time=300):
        ''' Default: 0.3sec fade in & out '''
        self.candSig = self.candSig.fade_in(fade_in_time).fade_out(fade_out_time)


    def overlay(self):
        print 'overlay'


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


if __name__ == '__main__':
    song = mash('../../test.pgz', '../../test.pgz')
    song.output('ori.wav')
    song.time_stretch(2)
    song.output('./mix.wav')
    #volume_adjust('ori.wav')
