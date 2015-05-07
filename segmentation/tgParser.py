"""
Prerequisites:
1. use 'tgTojson.praat' to convert TextGrid to Json format.

2. take care of encoding:
    dos2unix file

"""

## textgrid.py method is replaced since json is more convenient
##
## import textgrid as TG
##
## tgfile = 'laosheng-erhuang_01.TextGrid'
## f = open(tgfile, 'r')
## content = f.read()
## data = TG.TextGrid(content)
##
## print data.tiers[8].transcript[:500]

import json

class tgParser:
    def __init__(self, inputfile = 'laosheng-erhuang_01.json'):
        self.f = open(inputfile, 'r')
        self.data = json.load(self.f)
        self.f.close()

    def segVoice(self):
        banshi = self.data['tiers'][6]['intervals']
        syllable = self.data['tiers'][8]['intervals']
        luogu = self.data['tiers'][9]['intervals']
        voiceSeg = []
        percussionSeg = []
        jinghuSeg = []
        luoguSeg = []
        nonLuoguSeg = []

        for i in range(len(luogu)):
            if luogu[i]['text'] != '':
                luoguSeg.append([luogu[i]['xmin'], luogu[i]['xmax']])
            else:
                nonLuoguSeg.append([luogu[i]['xmin'], luogu[i]['xmax']])

        for i in range(len(syllable)):
            if syllable[i]['text'] == '':
                # empty syllable means either jinghu or percussion segment
                jinghuSeg.append([syllable[i]['xmin'], syllable[i]['xmax']])
            else:
                # annotation available means a character (voice)
                voiceSeg.append([syllable[i]['xmin'], syllable[i]['xmax']])

        for i in range(len(banshi)):
            if banshi[i]['text'] == '':
                # empty banshi means percussion segment
                percussionSeg.append([banshi[i]['xmin'], banshi[i]['xmax']])

        # exclude percussion segment from jinghu segment
        exclude = []
        for i in range(len(jinghuSeg)):
            for j in range(len(percussionSeg)):
                if jinghuSeg[i][0] < percussionSeg[j][0]:
                    if jinghuSeg[i][1] > percussionSeg[j][0] \
                       and jinghuSeg[i][1] <= percussionSeg[j][1]:
                        jinghuSeg[i][1] = percussionSeg[j][0]
                    elif jinghuSeg[i][1] > percussionSeg[j][1]:
                        jinghuSeg.append([jinghuSeg[i][0], percussionSeg[j][0]])
                        jinghuSeg.append([percussionSeg[j][1], jinghuSeg[i][1]])
                        exclude.append(i)

                if jinghuSeg[i][0] == percussionSeg[j][0]:
                    if jinghuSeg[i][1] <= percussionSeg[j][1]:
                        exclude.append(i)
                    else:
                        jinghuSeg[i][0] = percussionSeg[j][1]

                if jinghuSeg[i][0] > percussionSeg[j][0] \
                   and jinghuSeg[i][0] < percussionSeg[j][1]:
                    if jinghuSeg[i][1] <= percussionSeg[j][1]:
                        exclude.append(i)
                    else:
                        jinghuSeg[i][0] = percussionSeg[j][1]

        # use 'reversed' to prevent index out of range
        for i in reversed(exclude):
            del jinghuSeg[i]

        return voiceSeg, jinghuSeg, percussionSeg, luoguSeg, nonLuoguSeg


# if __name__ == '__main__':
#     test = tgParser()
