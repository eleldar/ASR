import threading
from random import choice
import os
from pathlib import Path

from functools import wraps
from api.tools.handler import Handler

# Local path settings
drive, path_and_file = os.path.splitdrive(Path(__file__).absolute())
path, file = os.path.split(path_and_file)
curdir = os.path.join(drive, path)

alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
get_file_prefix = lambda: ''.join(choice(alphabet) for _ in range(32))


def check_tasks(func):
    @wraps(func)
    def wrapper(self, task_id):
        if task_id not in self.task_ids:
            return 'bad id' 
        else:
            method_output = func(self, task_id)
            return method_output
    return wrapper


class Manager(object):
    def __init__(self):
        self.handlers = []
        self.task_ids = []


    def start(self, file):
        task_id = get_file_prefix()
        dir_local_path = os.path.join(curdir, '..', 'tempfiles', 'src') 
        file_path = os.path.join(
            dir_local_path,  
            f'{task_id}_{file.filename}'
        )
        file.save(file_path)
        handler = Handler()
        threading.Thread(target=handler.start, args=(file_path,), daemon=True).start()
        self.handlers.append(handler)
        self.task_ids.append(task_id)
        return task_id


    @check_tasks
    def get_results(self, task_id):
        handler_idx = self.task_ids.index(task_id)
        result = self.handlers[handler_idx].get_result()
        return result if result else 'on processing'


    def get_tasks(self):
        return self.task_ids
