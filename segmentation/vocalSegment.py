import os, sys

# Step 0: Change the Weka class adress to your setting
JAVAPATH = "/Applications/weka-3-6-11-apple-jvm.app/Contents/Resources" \
           + "/Java/weka.jar"

# inputFile = sys.argv[1]
# outputFile = sys.argv[2]
inputFile = './data/laoshengxipi04.wav'
outputFolder = './data/output'

os.makedirs(outputFolder)

## Step 1: Extract features from audio

print '\n... Step 1/6: Extracting features ...\n'

windowLength = 0.25
hopSize = windowLength    # no need for overlap

cmdExtractFeatures = 'python extractFeatures.py --inputFile ' + inputFile \
                     + ' --outputFolder ' + outputFolder + ' --length ' \
                     + str(windowLength) + ' --hopsize ' + str(hopSize)
os.system(cmdExtractFeatures)

## Step 2: Check feature files. Fill in missing files with preset files.

print '\n... Step 2/6: Checking features ...\n'

cmdFeatureCheck = 'python sigCheck.py ' + outputFolder + '/' \
                  + ' ./data/feature/nonvocal.sig'
os.system(cmdFeatureCheck)

## Step 3: Convert feature format to Weka .arff format

print '\n... Step 3/6: Converting feature format ...\n'

featureFolder = os.path.basename(inputFile)
featureFolder = featureFolder[:-4]
featureFolder = outputFolder + '/' + featureFolder

# set class to 'voice' as dummy data.
cmdConvertFormat = 'python essentiaToWeka.py --inputFolder ' + featureFolder \
                   + ' --label voice --clusters voice,instrument'
os.system(cmdConvertFormat)

## Step 4: Normalize features using training data

print '\n... Step 4/6: Normalizing features ...\n'
trainData = './data/feature/test_merge/merge.arff'
arffFile = featureFolder + '.arff'
cmdNormalize = "python normalize.py 'test' " + trainData + ' ' + arffFile \
               + ' ' + outputFolder
os.system(cmdNormalize)

# replace class name for some internal reasons
normFile = featureFolder + '_norm.arff'
cmdRenameClass = "sed -i '.original' 's/@ATTRIBUTE segment {voice, instrument}"\
                 "/@ATTRIBUTE segment {0.000000000000000000e+00," \
                 "1.000000000000000000e+00}/' " + normFile
os.system(cmdRenameClass)

## Step 5: Prediction

print '\n... Step 5/6: Predicting input data ...\n'

modelFile = './data/feature/test_merge/merge_norm.model'
predictionFile = outputFolder + '/prediction.txt'

# cmdPredict = 'java weka.classifiers.functions.SMO -T ' + normFile + ' -l ' \
#              + modelFile + ' -p 0 > ' + predictionFile
cmdPredict = 'java -cp ' + JAVAPATH + ' weka.classifiers.functions.SMO -T ' \
             + normFile + ' -l ' + modelFile + ' -p 0 > ' + predictionFile
os.system(cmdPredict)
# import time
# p = 0
# p = os.system(cmdPredict)
# while p == 0:
#     time.sleep(0.5)

# p = subprocess.Popen(['java', 'weka.classifiers.functions.SMO', '-T', \
#                       normFile, '-l', modelFile, '-p', '0'])
# p.wait()

## Step 6: Generate segmentation annotation file based on prediction

print '\n... Step 6/6: Generating annotation file ...\n'

f = open(predictionFile, 'r')
predOutput = f.readlines()
# trim unnecessary text
predOutput = predOutput[5 : -1]
f.close()

prediction = []
for line in predOutput:
    p = line.split()
    p = p[2].split(':')
    p = p[1]
    prediction.append(int(float(p)))

# smoothing prediction
predLen = len(prediction)
for i in range(predLen):
    smoothWindow = prediction[max(0, i - 2) : min(predLen, i + 3)]
    if prediction[i] == 1:    # 1:non-vocal, 0:vocal
        if sum(smoothWindow) <= 1:
            prediction[i] = 0
    elif max(prediction[i : min(predLen, i + 3)]) == 0:
        continue
    elif sum(smoothWindow) >= 3:
        prediction[i] = 1

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

annotationFile = outputFolder + '/segAnnotation.txt'
f = open(annotationFile, 'w')
label = ['V', 'N']    # V:vocal, N:non-vocal
for i in range(len(segStart)):
    anno = str(segStart[i]) + '\t' + str(segPred[i]) + '\t' \
           + str(segDuration[i]) + '\t' + label[segPred[i]] + '\n'
    f.write(anno)
f.close()
