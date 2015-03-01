from scipy.io import wavfile

inputFile = "./nonvoice.wav"
sNum = 10  # number of parts to split into

fs, x = wavfile.read(inputFile)
sLen = len(x) / sNum
for i in range(sNum):
    outputFile = inputFile[: -4] + str(i) + '.wav'
    if i != sNum - 1:
        seg = x[i*sLen : (i+1)*sLen]
        wavfile.write(outputFile, fs, seg)
    else:
        seg = x[i*sLen :]
        wavfile.write(outputFile, fs, seg)
    print "saving segment " + str(i)

