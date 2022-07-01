import threading
from random import choice, sample
import os
import sys
from pathlib import Path

from functools import wraps
from api.tools.handler import Handler

# Local path settings
drive, path_and_file = os.path.splitdrive(Path(__file__).absolute())
path, file = os.path.split(path_and_file)
curdir = os.path.join(drive, path)

# Temp solution!
MAX_THREADS = int(os.getenv('MAX_THREADS'))

alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz' 
name_power = 32
current_handlers = []
current_task_ids = []

def get_file_prefix(alphabet=alphabet, name_power=name_power):
    shuffled_alphabet = sample(alphabet, len(alphabet))
    return ''.join(choice(shuffled_alphabet) for _ in range(name_power))



def ids_from_local_path(dir_local_path):
    ids = []
    for file in os.listdir(dir_local_path):
        basename = os.path.basename(file)
        task_id, _ = basename.split('.')
        correct_id = True if not (
            set(task_id) - (set(task_id) & set(alphabet))
        ) and len (task_id) == name_power else False
        if correct_id:
            ids.append(task_id)
    return set(ids)



def check_tasks(func):
    @wraps(func)
    def wrapper(self, task_id):
        dir_local_path = os.path.join(curdir, '..', 'tempfiles', 'tgt')
        if task_id not in self.task_ids:
            return 'bad id' 
        else:
            method_output = func(self, task_id)
            return method_output
    return wrapper


class ActivePool:
    def __init__(self):
        super(ActivePool, self).__init__()
        self.active = []
        self.lock = threading.Lock()

    def makeActive(self, name):
        with self.lock:
            self.active.append(name)

    def makeInactive(self, name):
        with self.lock:
            self.active.remove(name)

# temp solution!
sem = threading.Semaphore(MAX_THREADS)
pool = ActivePool()


class Manager():
    def __init__(self):
        dir_local_path = os.path.join(curdir, '..', 'tempfiles', 'tgt')
        src_local_path = os.path.join(curdir, '..', 'tempfiles', 'src')
        src = {i.split('.')[0] for i in os.listdir(src_local_path)}
        self.task_ids = []
        self.handlers = []
        for file in os.listdir(dir_local_path):
            basename = os.path.basename(file)
            task_id, _ = basename.split('.')
            correct_id = True if not (
                set(task_id) - (set(task_id) & set(alphabet))
            ) and len (task_id) == name_power else False
            if correct_id and task_id not in src:
                self.task_ids.append(task_id)
                self.handlers.append(Handler(os.path.join(dir_local_path, basename)))
        for task_id, handler in zip(current_task_ids, current_handlers):
            if task_id not in self.task_ids:
                self.task_ids.append(task_id)
                self.handlers.append(handler)


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
        threading.Thread(target=handler.start, args=(file_path, sem, pool), daemon=True).start()
        current_handlers.append(handler)
        current_task_ids.append(task_id)
        self.handlers.append(handler)
        self.task_ids.append(task_id)
        return task_id


    @check_tasks
    def get_results(self, task_id):
        dir_tgt_path = os.path.join(curdir, '..', 'tempfiles', 'tgt')
        dir_src_path = os.path.join(curdir, '..', 'tempfiles', 'src')
        handler_idx = self.task_ids.index(task_id)
        try:
            return self.handlers[handler_idx].get_result()
        except TypeError:
            if task_id in ids_from_local_path(dir_tgt_path) or ids_from_local_path(dir_src_path):
                return 'on processing'
            return 'bad id'

    @check_tasks
    def delete_task(self, task_id):
        dir_local_path = os.path.join(curdir, '..', 'tempfiles', 'tgt')
        ids = ids_from_local_path(dir_local_path)
        if task_id in ids_from_local_path(dir_local_path) and self.get_results(task_id) != 'on processing':
            file = f'{task_id}.csv'
            file_path = os.path.join(dir_local_path, file) 
            os.remove(file_path)
            if task_id in current_task_ids:
                inx = current_task_ids.index(task_id)
                del current_handlers[inx]
                del current_task_ids[inx]
            self.__init__()
            return f'task {task_id} deleted'
        return 'bad id'


    def get_tasks(self):
        '''need check by media file'''
        self.__init__()
        return list(set(self.task_ids))
