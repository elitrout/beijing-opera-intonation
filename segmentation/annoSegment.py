"""
Separate singing voice, jinghu, percussion segments using annotation
"""

import numpy as np
import os
import subprocess
from scipy.io import wavfile
from tgParser import *

def voiceSegment(audiofile, annofile):
    fs, data = wavfile.read(audiofile)
    annotation = tgParser(annofile)
    voiceSeg, jinghuSeg, percussionSeg = annotation.segVoice()
    voice = np.array([], dtype = np.int16)
    jinghu = np.array([], dtype = np.int16)
    percussion = np.array([], dtype = np.int16)

    for i in range(len(voiceSeg)):
        segstart = fs * voiceSeg[i][0]
        segend = fs * voiceSeg[i][1]
        voice = np.append(voice, data[segstart : segend])

    for i in range(len(jinghuSeg)):
        segstart = fs * jinghuSeg[i][0]
        segend = fs * jinghuSeg[i][1]
        jinghu = np.append(jinghu, data[segstart : segend])

    for i in range(len(percussionSeg)):
        segstart = fs * percussionSeg[i][0]
        segend = fs * percussionSeg[i][1]
        percussion = np.append(percussion, data[segstart : segend])

    return fs, voice, jinghu, percussion


voiceMerge = np.array([], dtype = np.int16)
jinghuMerge = np.array([], dtype = np.int16)
percussionMerge = np.array([], dtype = np.int16)

audioDir = './data/arias'
jsonDir = './data/arias/annotation/json'
files = os.listdir(jsonDir)
for f in files:
    if f[-5:] == '.json':
        jsonfile = os.path.join(jsonDir, f)
        subprocess.call(['dos2unix', jsonfile])
        audiofile = audioDir + '/' + f[: -5] + '.wav'

        fs, v, j, p = voiceSegment(audiofile, jsonfile)
        if fs != 44100:
            print 'warning: sample rate is not 44100!'
        voiceMerge = np.append(voiceMerge, v)
        jinghuMerge = np.append(jinghuMerge, j)
        percussionMerge = np.append(percussionMerge, p)

wavfile.write('./data/arias/merge/voice.wav', 44100, voiceMerge)
wavfile.write('./data/arias/merge/jinghu.wav', 44100, jinghuMerge)
wavfile.write('./data/arias/merge/percussion.wav', 44100, percussionMerge)
