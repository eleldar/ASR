#!/usr/bin/env python3

import sys
import os
import wave
import subprocess

def video_decoder(file_path, sample_rate=16000):
    process = subprocess.Popen(['ffmpeg', '-loglevel', 'quiet', '-i', file_path,
        '-ar', str(sample_rate) , '-ac', '1', '-f', 's16le', '-'],
        stdout=subprocess.PIPE
    )
    return process
