#!/usr/bin/env python3
from statistics import quantiles


def get_dicts_list(string):
    '''list of dicts from vosk recogtition'''
    return eval(string)['result']


def vtt_format(data):
    '''VTT format string'''
    pass
    return 


def get_time_lists(data, step=1):
    '''
    списки пауз между словами:
    words_pauses - все паузы;
    actual_pauses - больше нуля и для превышающих поророг - step
    '''
    time_lists = {
        'all_pauses': [],
        'correct_pauses': []
    }
    for e, item in enumerate(data):
        if e < len(data) - 1:           
            pause = data[e+1]['start'] - data[e]['end']
            time_lists['all_pauses'].append(pause)
            if 0 < pause < step:
                time_lists['correct_pauses'].append(pause)
            elif pause > step:
                time_lists['correct_pauses'].append(step)
    return time_lists 



def replace_text(data):
    pauses = get_time_lists(data)
    qs = quantiles(pauses['correct_pauses'])
    pauses['all_pauses'].append(0)
    words = [word['word'] for word in data]
    len_words = len(words)
    text = ''
    for e, (word, pause) in enumerate(zip(words, pauses['all_pauses'])):
        if e == 0 or text[-2] == ".":
            text += word.capitalize()
        else:
            text += word
        if pause > qs[2]:
            text += '. '
        elif pause > qs[1]:
            text += ', '
        elif e == len_words - 1:
            text += '.'
        else:
            text += ' '
    return text


if __name__ == '__main__':
    pass
