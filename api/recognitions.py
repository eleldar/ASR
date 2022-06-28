#!/usr/bin/env python3
import os
import sys
from vosk import Model, KaldiRecognizer, SetLogLevel
from pathlib import Path
import subprocess
import csv 

# cirrent paths for different OS
drive, path_and_file = os.path.splitdrive(Path(__file__).absolute())
path, file = os.path.split(path_and_file)
curdir = os.path.join(drive, path)

# import tools
sys.path.append(curdir)
from tools.preprocess import video_decoder
from tools.postprocess import vtt_format, get_dicts_list 


# models init
models_path = os.path.join(curdir, 'models')
SetLogLevel(-1) # keep init message
models = {
    'en': Model(os.path.join(models_path, 'en')),
}


def make_data_file(file_name, headers):
    '''always make new file'''
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(f'{",".join(headers)}\n')


def save_data(string, file_name, headers):
    '''save to csv; need refactoring'''
    dicts = get_dicts_list(string)
    if dicts:
        with open(file_name, 'a', newline='', encoding='utf-8') as f:
            dictwriter_object = csv.DictWriter(f, fieldnames=headers)
            for dct in dicts:
                row = {
                    "word": dct["word"],"start": dct["start"], 
                    "end": dct["end"], "conf": dct["conf"]
                }
                dictwriter_object.writerow(row)


def read_data(data_file):
    '''read csv file and return list of dicts'''
    dicts = []
    try:
        with open(data_file) as f:
            reader = csv.DictReader(f)
            for row in reader:
                dicts.append(row)
        return dicts
    except FileNotFoundError:
        return


def recognize(file_path, language='en'):
    '''giperparameters, recognize, save, read and split text file'''
    sample_rate = 16000
    model = models[language]
    rec = KaldiRecognizer(model, sample_rate)
    rec.SetWords(True)
    rec.SetPartialWords(True)
    process = video_decoder(file_path, sample_rate) 

    # recognize and save to csv file
    drive, path_and_file = os.path.splitdrive(Path(__file__).absolute())
    path, file = os.path.split(path_and_file)
    curdir = os.path.join(drive, path)

    data_file = os.path.splitext(os.path.basename(file_path))[0] + '.csv'
    data_file = os.path.join(curdir, 'tempfiles', 'tgt', data_file)

    headers = ["word", "start", "end", "conf"]
    make_data_file(data_file, headers)

    while True:
        frame = process.stdout.read(4000)
        if len(frame) == 0:
            break
        if rec.AcceptWaveform(frame):
            output = rec.Result() 
            save_data(output, data_file, headers)
    output = rec.FinalResult()
    save_data(output, data_file, headers)
    os.remove(file_path)
    return data_file 


if __name__ == '__main__':
    try:
        file_path = sys.argv[1]
        print(recognize(file_path))
    except IndexError:
        print('Not fount file mp4') 
