"""
Separate luogu and non-luogu segments using annotation
"""

import numpy as np
import os
import subprocess
from scipy.io import wavfile
from tgParser import *

def luoguSegment(audiofile, annofile):
    fs, data = wavfile.read(audiofile)
    annotation = tgParser(annofile)
    voiceSeg, jinghuSeg, percussionSeg, luoguSeg, nonLuoguSeg = annotation.segVoice()
    luogu = np.array([], dtype = np.int16)
    nonLuogu = np.array([], dtype = np.int16)

    for i in range(len(luoguSeg)):
        segstart = fs * luoguSeg[i][0]
        segend = fs * luoguSeg[i][1]
        luogu = np.append(luogu, data[segstart : segend])

    for i in range(len(nonLuoguSeg)):
        segstart = fs * nonLuoguSeg[i][0]
        segend = fs * nonLuoguSeg[i][1]
        nonLuogu = np.append(nonLuogu, data[segstart : segend])

    return fs, luogu, nonLuogu


luoguMerge = np.array([], dtype = np.int16)
nonLuoguMerge = np.array([], dtype = np.int16)

audioDir = './data/arias'
jsonDir = './data/arias/annotation/json'
files = os.listdir(jsonDir)
for f in files:
    if f[-5:] == '.json':
        jsonfile = os.path.join(jsonDir, f)
        subprocess.call(['dos2unix', jsonfile])
        audiofile = audioDir + '/' + f[: -5] + '.wav'

        fs, lg, nlg = luoguSegment(audiofile, jsonfile)
        if fs != 44100:
            print 'warning: sample rate is not 44100!'
        luoguMerge = np.append(luoguMerge, lg)
        nonLuoguMerge = np.append(nonLuoguMerge, nlg)

wavfile.write('./data/arias/merge/luogu.wav', 44100, luoguMerge)
wavfile.write('./data/arias/merge/nonLuogu.wav', 44100, nonLuoguMerge)
