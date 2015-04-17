#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
from sys import platform as _platform

"""
A wrap-up for vocal/non-vocal segmentation using pre-trained model. It takes an 
audio file as input and generates the segmentation annotation file which can be 
opened with SonicVisualiser.

Usage:
python vocalSegment.py inputFile

Prerequisites: 
1. Weka (check the Weka JAVAPATH below)
2. Essentia

"""

def extractFeature(inputFile, outputFolder, windowLength, hopSize):
    cmdExtractFeatures = 'python extractFeatures.py --inputFile ' + inputFile \
                         + ' --outputFolder ' + outputFolder + ' --length ' \
                         + str(windowLength) + ' --hopsize ' + str(hopSize)
    os.system(cmdExtractFeatures)

def checkFeature(outputFolder):
    dummyFile = './data/feature/nonvocal.sig'
    cmdFeatureCheck = 'python sigCheck.py ' + outputFolder + '/ ' + dummyFile
    os.system(cmdFeatureCheck)

def convertFormat(featureFolder):
    # set class to 'voice' as dummy data.
    cmdConvertFormat = 'python essentiaToWeka.py --inputFolder ' + featureFolder \
                       + ' --label voice --clusters voice,instrument'
    os.system(cmdConvertFormat)

def normalize(normvalueFile, arffFile, outputFolder, normFile):
    cmdNormalize = "python normalize.py 'test' " + normvalueFile + ' ' + arffFile \
                   + ' ' + outputFolder
    os.system(cmdNormalize)

    if _platform == 'darwin':
        cmdRenameClass = "sed -i '.original' 's/@ATTRIBUTE segment {voice, instrument}"\
                         "/@ATTRIBUTE segment {0.000000000000000000e+00," \
                         "1.000000000000000000e+00}/' " + normFile
    elif _platform == "linux" or _platform == "linux2":
        cmdRenameClass = "sed -i 's/@ATTRIBUTE segment {voice, instrument}"\
                         "/@ATTRIBUTE segment {0.000000000000000000e+00," \
                         "1.000000000000000000e+00}/' " + normFile
    else:
        print "\nError: Only support Mac and Linux"

    os.system(cmdRenameClass)

def predict(JAVAPATH, normFile, modelFile, predictionFile):
    # cmdPredict = 'java -cp ' + JAVAPATH + ' weka.classifiers.functions.SMO -T ' \
    #              + normFile + ' -l ' + modelFile + ' -p 0 -distribution -M -N 2 > ' + predictionFile
    cmdPredict = 'java -cp ' + JAVAPATH + ' weka.classifiers.functions.SMO -T ' \
                 + normFile + ' -l ' + modelFile + ' -p 0 > ' + predictionFile
    os.system(cmdPredict)

def smoothPrediction(prediction):
    """ Smooth prediction """

    predSmooth = prediction[:]
    predLen = len(predSmooth)

    for i in range(predLen):
        smoothWindow = predSmooth[max(0, i - 2) : min(predLen, i + 3)]
        if predSmooth[i] == 1:    # 1:non-vocal, 0:vocal
            if sum(smoothWindow) <= 1:
                predSmooth[i] = 0
        elif max(predSmooth[i : min(predLen, i + 3)]) == 0:
            continue
        elif sum(smoothWindow) >= 3:
            predSmooth[i] = 1

    return predSmooth

def annotationGen(prediction, annotationFile, windowLength):
    """ Write annotation to file """

    predLen = len(prediction)
    segStart = []
    segDuration = []
    segPred = []
    segStart.append(0.0)
    for i in range(1, predLen):
        if prediction[i] != prediction[i - 1]:
            segPred.append(prediction[i - 1])
            segDuration.append(i * windowLength - segStart[-1])
            segStart.append(i * windowLength)
    segDuration.append(predLen * windowLength - segStart[-1])
    segPred.append(prediction[-1])

    f = open(annotationFile, 'w')
    label = ['V', 'P', 'J']    # V:vocal, P:percussion, J:jinghu
    for i in range(len(segStart)):
        anno = str(segStart[i]) + '\t' + str(segPred[i]) + '\t' \
               + str(segDuration[i]) + '\t' + label[segPred[i]] + '\n'
        f.write(anno)
    f.close()


if __name__ ==  '__main__':

    ## Step 0: Change the Weka class adress to your setting if necessary
    if _platform == "darwin":
        JAVAPATH = "/Applications/weka-3-6-11-apple-jvm.app/Contents/Resources" \
                   + "/Java/weka.jar"
    elif _platform == "linux" or _platform == "linux2":
        JAVAPATH = "/usr/share/java/weka.jar"
    else:
        print "\nError: Only support Mac and Linux"

    inputFile = sys.argv[1]
    # outputFolder = sys.argv[2]
    # inputFile = './data/laoshengxipi04.wav'
    outputFolder = './data/output_' + os.path.basename(inputFile)[:-4]

    os.makedirs(outputFolder)

    ## Step 1: Extract features from audio

    print '\n... Step 1/6: Extracting features ...\n'

    windowLength = 0.25
    hopSize = windowLength    # no need for overlap

    extractFeature(inputFile, outputFolder, windowLength, hopSize)

    ## Step 2: Check feature files. Fill in missing files with preset files.

    print '\n... Step 2/6: Checking features ...\n'

    checkFeature(outputFolder)

    ## Step 3: Convert feature format to Weka .arff format

    print '\n... Step 3/6: Converting feature format ...\n'

    featureFolder = os.path.basename(inputFile)
    featureFolder = featureFolder[:-4]
    featureFolder = outputFolder + '/' + featureFolder

    convertFormat(featureFolder)

    ## Step 4: Normalize features using training data

    print '\n... Step 4/6: Normalizing features ...\n'
    # trainData = './data/feature/test_merge/merge.arff'
    VNnormvalueFile = './data/feature/test_merge/merge_norm_normvalue.pkl'
    VNarffFile = featureFolder + '.arff'

    # replace class name for some internal reasons
    normFile = featureFolder + '_norm.arff'

    normalize(VNnormvalueFile, VNarffFile, outputFolder, normFile)

    VNnormFile = normFile[:-5] + 'VN.arff'
    cmdRenameNormfile = 'mv ' + normFile + ' ' + VNnormFile
    os.system(cmdRenameNormfile)

    # trainData = './data/arias/merge/merge.arff'
    JPnormvalueFile = './data/arias/merge/merge_norm_normvalue.pkl'
    JParffFile = featureFolder + '.arff'

    # replace class name for some internal reasons
    normFile = featureFolder + '_norm.arff'

    normalize(JPnormvalueFile, JParffFile, outputFolder, normFile)

    JPnormFile = normFile[:-5] + 'JP.arff'
    cmdRenameNormfile = 'mv ' + normFile + ' ' + JPnormFile
    os.system(cmdRenameNormfile)

    ## Step 5: Prediction

    print '\n... Step 5/6: Predicting input data ...\n'

    VNmodelFile = './data/feature/test_merge/merge_norm.model'
    VNpredictionFile = outputFolder + '/predictionVN.txt'
    JPmodelFile = './data/arias/merge/jinghuPercussion.model'
    JPpredictionFile = outputFolder + '/predictionJP.txt'

    predict(JAVAPATH, VNnormFile, VNmodelFile, VNpredictionFile)
    predict(JAVAPATH, JPnormFile, JPmodelFile, JPpredictionFile)

    ## Step 6: Generate segmentation annotation file based on prediction

    print '\n... Step 6/6: Generating annotation file ...\n'

    # read vocal/non-vocal prediction
    f = open(VNpredictionFile, 'r')
    VNpredOutput = f.readlines()
    # trim unnecessary text
    VNpredOutput = VNpredOutput[5 : -1]
    f.close()

    VNprediction = []
    for line in VNpredOutput:
        p = line.split()
        p = p[2].split(':')
        p = p[1]
        VNprediction.append(int(float(p)))

    # smooth prediction
    VNpredSmooth = smoothPrediction(VNprediction)

    # read jinghu/percussion prediction file
    f = open(JPpredictionFile, 'r')
    JPpredOutput = f.readlines()
    # trim unnecessary text
    JPpredOutput = JPpredOutput[5 : -1]
    f.close()

    JPprediction = []
    for line in JPpredOutput:
        p = line.split()
        p = p[2].split(':')
        p = p[1]
        JPprediction.append(int(float(p)))

    # merge VN and JP prediction
    mergePrediction = VNpredSmooth[:]
    for i in range(len(mergePrediction)):
        if mergePrediction[i] == 1:
            # if non-vocal, then check it's jinghu or percussion
            mergePrediction[i] = JPprediction[i] + 1    # percussion becomes 1, jinghu becomes 2
        
    annotationGen(VNpredSmooth, outputFolder + '/segAnnotationVNSmooth.txt', windowLength)
    annotationGen(mergePrediction, outputFolder + '/segAnnotationMerge.txt', windowLength)
