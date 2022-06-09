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
from tools.postprocess import vtt_format, get_dicts_list, replace_text


# models init
models_path = os.path.join(curdir, 'models')
SetLogLevel(-1) # keep init message
models = {
    'en': Model(os.path.join(models_path, 'en')),
}


def save_data(string, storage):
    '''
    temp solution for data save; will use temp file;
    get time word pause
    ! need list of dicts !
    '''
    dicts = get_dicts_list(string)
    storage.extend(dicts)


def recognize(language, file_path):
    sample_rate = 16000
    model = models[language]
    rec = KaldiRecognizer(model, sample_rate)
    rec.SetWords(True)
    rec.SetPartialWords(True)
    process = video_decoder(file_path, sample_rate) 
    temp_storage = [] # need list of dicts
    while True:
        data = process.stdout.read(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            save_data(rec.Result(), temp_storage)
    save_data(rec.FinalResult(), temp_storage)
    return replace_text(temp_storage)


if __name__ == '__main__':
    language = 'en'
    file_path = sys.argv[1]
    print(recognize(language, file_path))
