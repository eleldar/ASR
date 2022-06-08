#!/usr/bin/env python3
import os
import sys
from vosk import Model, KaldiRecognizer, SetLogLevel
from pathlib import Path
import subprocess

# cirrent paths for different OS
drive, path_and_file = os.path.splitdrive(Path(__file__).absolute())
path, file = os.path.split(path_and_file)
curdir = os.path.join(drive, path)

# import tools
sys.path.append(curdir)
from tools.preprocess import video_decoder

# models init
models_path = os.path.join(curdir, 'models')
SetLogLevel(-1) # keep init message
models = {
    'en': Model(os.path.join(models_path, 'en')),
}


def recognize(language, file_path):
    sample_rate = 16000
    model = models[language]
    rec = KaldiRecognizer(model, sample_rate)
    rec.SetWords(True)
    rec.SetPartialWords(True)
    process = video_decoder(file_path, sample_rate) 
    while True:
        data = process.stdout.read(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            tmp = eval(rec.Result())
            print(tmp['result'])
        else:
            pass
#            print(rec.PartialResult())
    tmp = eval(rec.FinalResult())
    print(tmp['result'])


if __name__ == '__main__':
    language = 'en'
    file_path = sys.argv[1]
    recognize(language, file_path)
