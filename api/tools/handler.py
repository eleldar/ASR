import os
from pathlib import Path
import filetype as ft
import moviepy.editor as mp
from api.recognitions import recognize, read_data
from tools.postprocess import vtt_format, get_dicts_list

# cirrent paths for different OS
drive, path_and_file = os.path.splitdrive(Path(__file__).absolute())
path, file = os.path.split(path_and_file)
curdir = os.path.join(drive, path)


def get_file_info(filetype):
    '''file info from filetype.guess method'''
    if filetype.split('/')[0] == 'video':
        with mp.VideoFileClip(file) as f:
            return {
                'fps': f.fps, 'filename': f.filename,
                'aspect_ratio': f.aspect_ratio, 'duration': f.duration,
                'end': f.end, 'hight': f.h, 'rotation': f.rotation,
                'size': f.size, 'start': f.start, 'weight': f.w
            }
    elif self.file_info['filetype'].split('/')[0] == 'audio':
        with mp.AudioFileClip(file) as f:
            return {
                'buffersize': f.buffersize, 'duration': f.duration, 
                'end': f.end, 'fps': f.fps, 'nchannels': f.nchannels,
                'start': f.start
            }
    return None



class Handler():
    def __init__(self, data_file=None):
        self.file_info = {'data_file': data_file} 

    def start(self, file):
        self.file_info['filetype'] = ft.guess(file).mime if ft.guess(file) else None       
        self.file_info['data_file'] = recognize(file)
        print('Debuger result form handler:', self.file_info['data_file'])


    def get_result(self):
        '''baseline'''
        data_file = self.file_info['data_file']
        return vtt_format(read_data(data_file))


