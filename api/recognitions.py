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
    with open(file_name, 'a', newline='', encoding='utf-8') as f:
        dictwriter_object = csv.DictWriter(f, fieldnames=headers)
        for dct in dicts:
            row = {
                "word": dct["word"],"start": dct["start"], 
                "end": dct["end"], "conf": dct["conf"]
            }
            dictwriter_object.writerow(row)


def read_data(data_file='data.csv'):
    '''read csv file and return list of dicts'''
    dicts = []
    with open(data_file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            dicts.append(row)
    return dicts


def recognize(language, file_path, data_file='data.csv'):
    '''giperparameters, recognize, save, read and split text file'''
    sample_rate = 16000
    model = models[language]
    rec = KaldiRecognizer(model, sample_rate)
    rec.SetWords(True)
    rec.SetPartialWords(True)
    process = video_decoder(file_path, sample_rate) 

    # recognize and save to csv file
    headers = ["word", "start", "end", "conf"]
    make_data_file(data_file, headers)

    while True:
        frame = process.stdout.read(4000)
        if len(frame) == 0:
            break
        if rec.AcceptWaveform(frame):
            save_data(rec.Result(), data_file, headers)
    save_data(rec.FinalResult(), data_file, headers)

    # read data
    return vtt_format(read_data(data_file))


if __name__ == '__main__':
    language = 'en'
    try:
        file_path = sys.argv[1]
        data_file = 'data.csv'
        print(recognize(language, file_path, data_file))
    except IndexError:
        print('Not fount file mp4') 
