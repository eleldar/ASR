import threading
from random import randint
import os

from functools import wraps
from src.handler import Handler


def check_tasks(func):
    @wraps(func)
    def wrapper(self, task_id):
        if task_id not in self.task_ids:
            return '', f'Task {task_id} doesn\'t exist.', 0, 0
        else:
            method_output = func(self, task_id)
            return method_output
    return wrapper


class Manager(object):
    def __init__(self):
        self.handlers = []
        self.current_handler = -1
        self.task_ids = []

    def start(self, file):
        task_id = randint(0, 2**31)
        file_path = f'{task_id}.mp4'
        with open(file_path, 'wb') as f:
            f.write(file.stream.read())

        handler = Handler()
        threading.Thread(target=handler.start, args=(file_path,), daemon=True).start()
        # self.current_handler = 0 if self.current_handler == -1 else self.current_handler
        self.handlers.append(handler)
        self.task_ids.append(task_id)
        return task_id

    @check_tasks
    def get_results(self, task_id):
        handler_idx = self.task_ids.index(task_id)
        result = self.handlers[handler_idx].get_result()  # translated result in API
        return result

    @check_tasks
    def get_status(self, task_id):
        handler_idx = self.task_ids.index(task_id)
        error, current_frame, num_frames = self.handlers[handler_idx].get_status()  # obtained status
        if current_frame >= num_frames or error != '':
            os.remove(f'{task_id}.mp4')
        return error, current_frame, num_frames

    def get_tasks(self):
        return self.task_ids