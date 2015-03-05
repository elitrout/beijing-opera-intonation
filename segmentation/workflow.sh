#!/bin/bash

## 1. Feature extraction
# Essentia memory leak!!!
# python extractFeatures.py --inputFolder ./ --outputFolder ./ --length 0.5 --hopsize 0.1
nohup python extractFeatures.py --inputFile ./data/nonvoice0.wav --outputFolder ./data --length 0.5 --hopsize 0.1 &
# ...
nohup python extractFeatures.py --inputFile ./data/voice0.wav --outputFolder ./data --length 0.5 --hopsize 0.1 &
# ...


## 2. Check sig files
# use one file in the same class as insert.sig
# python sigCheck.py sig_folder insert.sig &
python sigCheck.py ./data/feature/test_voice/ ./data/feature/voice0_000.sig
python sigCheck.py ./data/feature/test_nonvoice/ ./data/feature/nonvoice0_0000.sig

nohup python essentiaToWeka.py --inputFolder ./data/feature/test_voice/voice0 --label voice --clusters voice,instrument &
# ...
nohup python essentiaToWeka.py --inputFolder ./data/feature/test_nonvoice/nonvoice0 --label instrument --clusters voice,instrument &
# ...

# append arff files. seems that this cannot deal with nan/inf situations. use shell command instead.
# java weka.core.Instances append filename1 filename2 > output-file
# the feature value starts at line 192
cp ./data/feature/test_voice/voice0.arff ./data/feature/test_voice/voice.arff
# append features from line 192
sed -n '192,$p' ./data/feature/test_voice/voice1.arff >> ./data/feature/test_voice/voice.arff
sed -n '192,$p' ./data/feature/test_voice/voice2.arff >> ./data/feature/test_voice/voice.arff
# ...
cp ./data/feature/test_nonvoice/nonvoice0.arff ./data/feature/test_nonvoice/nonvoice.arff
sed -n '192,$p' ./data/feature/test_nonvoice/nonvoice1.arff >> ./data/feature/test_nonvoice/nonvoice.arff
# ...
# append to classes
mkdir data/feature/test_merge
cp ./data/feature/test_voice/voice.arff ./data/feature/test_merge/merge.arff
sed -n '192,$p' ./data/feature/test_nonvoice/nonvoice.arff >> ./data/feature/test_merge//merge.arff

# 3. Normalize features
python normalize.py 'train' ./data/feature/test_merge/merge.arff ./data/feature/test_merge/merge_norm.arff
# the fix label data type (string to REAL) caused by normalize.py
# change from "@ATTRIBUTE segment {voice, instrument}" to "@ATTRIBUTE segment {0.000000000000000000e+00, 1.000000000000000000e+00}"
