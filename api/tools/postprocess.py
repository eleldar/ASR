#!/usr/bin/env python3
from statistics import quantiles
from random import randint

def get_dicts_list(string):
    '''list of dicts from vosk recogtition'''
    return eval(string)['result']


def vtt_format(data):
    '''VTT format string'''
    lists = [i for i in replace_text(data).split('\n')]
    times = lists[0::2]
    strings = lists[1::2]
    result = ''
    for time, string in zip(times, strings):
        string = string.replace('.', '')
        string = string.replace(',', '')
        result += time + '\n'
        result += string.lower() + '\n'
        result += '\n'
    return result 


def get_time_lists(data):
    '''
    списки пауз между словами:
    words_pauses - все паузы;
    actual_pauses - больше нуля и для превышающих поророг - step
    '''
    sample = set()
    steps = []
    while len(steps) < int(len(data) * 0.2):
        i = randint(0, len(data) - 2)
        pause = float(data[i+1]['start']) - float(data[i]['end'])
        if pause and i not in sample:
            sample.add(i)
            steps.append(pause)
    step = quantiles(steps, n=100)[94]
    time_lists = {
        'all_pauses': [],
        'correct_pauses': []
    }
    for e, item in enumerate(data):
        if e < len(data) - 1:           
            pause = float(data[e+1]['start']) - float(data[e]['end'])
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
    len_words = len(data)
    text = ''
    start = None
    for e, (row, pause) in enumerate(zip(data, pauses['all_pauses'])):
        if e == 0 or text[-2] == ".":
            text += row['word'].capitalize()
            start = row['start']
        else:
            text += row['word']
        if pause > qs[2]:
            time = ' --> '.join([start, row['end']]) + '\n'
            if text.find('.') != -1:
                inx = text.rfind('.')
                text = text[:inx + 2] + '\n' + time + text[inx + 2:] + '. '
            else:
                text = time + text + '. '
        elif pause > qs[1]:
            text += ', '
        elif e == len_words - 1:
            time = ' --> '.join([start, row['end']]) + '\n'
            inx = text.rfind('.')
            text = text[:inx + 2] + '\n' + time + text[inx + 2:] + '.'
        else:
            text += ' '
    return text


if __name__ == '__main__':
    pass
