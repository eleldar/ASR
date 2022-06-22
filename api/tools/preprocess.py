#!/usr/bin/env python3

import sys
import os
import wave
import subprocess
from pathlib import Path
import moviepy.editor as mp
import shutil
from random import randint


drive, path_and_file = os.path.splitdrive(Path(__file__).absolute())
path, file = os.path.split(path_and_file)                                                                            
curdir = os.path.join(drive, path)


def video_decoder(file_path, sample_rate=16000):
    process = subprocess.Popen(['ffmpeg', '-loglevel', 'quiet', '-i', file_path, 
        '-ar', str(sample_rate) , '-ac', '1', '-f', 's16le', '-'],
        stdout=subprocess.PIPE
    )
    return process


def video_splitter(file_path, parts=3, tgt_type='mp4'):
    """
    Split video to parts (default parts=5).
    For get video use tgt_type='mp4', for get audio use tgt_type='wav'.
    """
    video_types = {'mp4'}
    audio_types = {'wav'}
    video = mp.VideoFileClip(file_path)
    distance = video.end // parts
    basename = os.path.splitext(os.path.basename(file_path))[0]
    target_dir = os.path.join(curdir, '..', 'tempfiles', 'src', f'{basename}')
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir, ignore_errors=True)
    os.makedirs(target_dir)
    start = video.start
    end = distance if (video.end > distance) else video.end
    part = 0
    while True:
        part += 1
        tmp = video.subclip(start, end)

        if tgt_type in video_types:
            tmp.write_videofile(os.path.join(target_dir, 
                f'{str(part).zfill(3)}_{basename}.{tgt_type}')
            )
        elif tgt_type in audio_types:
            tmp.audio.write_audiofile(os.path.join(target_dir, 
                f'{str(part).zfill(3)}_{basename}.{tgt_type}')
            )

        if end == video.end:
            break

        start = start + distance
        end = end + distance if (end + distance * 2) <= video.end else video.end 
       

if __name__ == '__main__':
    file_path = 'videoplayback.mp4'
    print(video_splitter(file_path))
