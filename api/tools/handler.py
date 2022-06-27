import os
from datetime import datetime, timedelta
from typing import List, Tuple
import moviepy.editor as mp
from api.tools.utils import frames_diff, get_time, get_mask
from pathlib import Path
from api.recognitions import recognize
import filetype as ft

TIME_MASK = "%H:%M:%S,%f"

class Handler(object):
    def __init__(self):
        self.text = None
        self.file_info = {}

    def start(self, file):
        file_info = {}
        self.file_info = {
            'filetype': ft.guess(file).mime if ft.guess(file) else None
        }
        if self.file_info['filetype'].split('/')[0] == 'video':
            with mp.VideoFileClip(file) as f:
                file_info = {
                    'fps': f.fps, 'filename': f.filename,
                    'aspect_ratio': f.aspect_ratio, 'duration': f.duration,
                    'end': f.end, 'hight': f.h, 'rotation': f.rotation,
                    'size': f.size, 'start': f.start, 'weight': f.w
                }
        elif self.file_info['filetype'].split('/')[0] == 'audio':
            with mp.AudioFileClip(file) as f:
                file_info = {
                    'buffersize': f.buffersize, 'duration': f.duration, 
                    'end': f.end, 'fps': f.fps, 'nchannels': f.nchannels,
                    'start': f.start
                }
        else:
            return False

        self.file_info.update(file_info)
        text = recognize(file)
        self.text = text if text != None else 'No text found :('
        print('Debuger result:', self.text)


    def get_result(self):
        '''baseline'''
        return self.text if self.text else 'In progress. Please wait :)'


    def get_status(self):
        '''baseline'''
        return self.text

