import threading
from random import choice, sample
import os
from pathlib import Path

from functools import wraps
from api.tools.handler import Handler

# Local path settings
drive, path_and_file = os.path.splitdrive(Path(__file__).absolute())
path, file = os.path.split(path_and_file)
curdir = os.path.join(drive, path)

alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz' 
name_power = 32

def get_file_prefix(alphabet=alphabet, name_power=name_power):
    shuffled_alphabet = sample(alphabet, len(alphabet))
    return ''.join(choice(shuffled_alphabet) for _ in range(name_power))


def check_tasks(func):
    @wraps(func)
    def wrapper(self, task_id):
        if task_id not in self.task_ids:
            return 'bad id' 
        else:
            method_output = func(self, task_id)
            return method_output
    return wrapper


class Manager():
    def __init__(self):
        dir_local_path = os.path.join(curdir, '..', 'tempfiles', 'tgt')
        self.task_ids = []
        self.handlers = []
        for file in os.listdir(dir_local_path):
            basename = os.path.basename(file)
            task_id, _ = basename.split('.')
            correct_id = True if not (
                set(task_id) - (set(task_id) & set(alphabet))
            ) and len (task_id) == name_power else False
            if correct_id:
                self.task_ids.append(task_id)
                self.handlers.append(Handler(os.path.join(dir_local_path, basename)))


    def start(self, file):
        task_id = get_file_prefix()
        dir_local_path = os.path.join(curdir, '..', 'tempfiles', 'src') 
        file_extension = os.path.splitext(os.path.basename(file.filename))[-1]

        file_path = os.path.join(
            dir_local_path,  
            f'{task_id}{file_extension}'
        )
        file.save(file_path)
        handler = Handler()
        threading.Thread(target=handler.start, args=(file_path,), daemon=True).start()
        self.handlers.append(handler)
        self.task_ids.append(task_id)
        return task_id


    @check_tasks
    def get_results(self, task_id):
        dir_local_path = os.path.join(curdir, '..', 'tempfiles', 'tgt')
        handler_idx = self.task_ids.index(task_id)
        try:
            return self.handlers[handler_idx].get_result()
        except TypeError:
            return 'on processing'


    def get_tasks(self):
        return self.task_ids
