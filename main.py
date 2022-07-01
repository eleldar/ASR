import os
import sys
from pathlib import Path
from flask import Flask
from flask_restx import Resource, Api, fields
from flask_cors import CORS, cross_origin
from werkzeug.datastructures import FileStorage
from api.recognitions import recognize
from time import time
from datetime import timedelta
from argparse import ArgumentParser

# Local path settings
drive, path_and_file = os.path.splitdrive(Path(__file__).absolute())
path, file = os.path.split(path_and_file)
curdir = os.path.join(drive, path)

app = Flask(__name__)
app.config['RESTPLUS_MASK_SWAGGER'] = False
api = Api(
    app, 
    version='1.0',
    title='ASR',
    doc="/api",
)

CORS(app)
namespace = api.namespace('recognition', 
#    description='ASR'
)

start_response = api.model('StartResponse', {
    'task_id': fields.String
})


task_info = api.model('TaskInfo', {
    'id': fields.String
})


result_response = api.model('ResultResponse', {
    'result': fields.String
})


status_response = api.model('StatusResponse', {
    'status': fields.String
})

tasks_response = api.model('TasksResponse', {
    'task_list': fields.List(fields.String)
})


delete_task = api.model('DeleteTask', {
    'result': fields.String
})


upload_parser = api.parser()
upload_parser.add_argument('file', location='files',
                            type=FileStorage, required=True
                          )


@namespace.route('/start')
class DetectApi(Resource):
    @namespace.doc('VideoHandleStart')
    @namespace.expect(upload_parser)
    @namespace.marshal_with(start_response, code=201)
    def post(self):
        args = upload_parser.parse_args()
        file = args['file']

        task_id = manager.start(file)
        return {'task_id': task_id}, 201


@namespace.route('/result')
class DetectApi(Resource):
    @namespace.doc('ProcessedText')
    @namespace.expect(task_info)
    @namespace.marshal_with(result_response, code=200)
    @namespace.response(404, 'No results')
    def post(self):
        data = api.payload
        task_id = data['id']
        result = manager.get_results(task_id=task_id)
        if result == "bad id" or result == "on processing":
            return {'result': result}, 404
        else:
            return {'result': result}, 200


@namespace.route('/getstatus')
class DetectApi(Resource):
    @namespace.doc('StatusResponse')
    @namespace.expect(task_info)
    @namespace.marshal_with(status_response, code=200)
    def post(self):
        data = api.payload
        task_id = data['id']
        result = manager.get_results(task_id=task_id)
        if result == "bad id" or result == "on processing":
            return {'status': result}, 200
        else:
            return {'status': 'done'}, 200


@namespace.route('/tasks')
class DetectApi(Resource):
    @namespace.doc('AllTaskIDs')
    @namespace.marshal_with(tasks_response, code=200)
    def get(self):
        tasks_ids = manager.get_tasks()
        return {'task_list': tasks_ids}, 200


@namespace.route('/delete')
class DetectApi(Resource):
    @namespace.doc('DelTask')
    @namespace.expect(task_info)
    @namespace.marshal_with(delete_task, code=200)
    def delete(self):
        data = api.payload
        task_id = data['id']
        result = manager.delete_task(task_id=task_id)
        return {'result': result}, 200


if __name__ == '__main__':
    def ids_from_local_path(dir_local_path):
        ids = []
        for file in os.listdir(dir_local_path):
            alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
            name_power = 32
            basename = os.path.basename(file)
            task_id, ext = basename.split('.')
            correct_id = True if not (
                set(task_id) - (set(task_id) & set(alphabet))
            ) and len (task_id) == name_power else False
            if correct_id:
                ids.append(task_id)
        return set(ids)
    dir_src_path = os.path.join(curdir, 'api', 'tempfiles', 'src')
    dir_tgt_path = os.path.join(curdir, 'api', 'tempfiles', 'tgt')
    files_src_path = set(ids_from_local_path(dir_src_path))
    files_tgt_path = set(ids_from_local_path(dir_tgt_path))
    delete_tgt_list = files_src_path & files_tgt_path 

    for file in os.listdir(dir_src_path):
        basename = os.path.basename(file)
        task_id, ext = basename.split('.')
        if task_id in files_src_path:
            file = os.path.join(dir_src_path, file)  
            os.remove(file)

    for file in os.listdir(dir_tgt_path):
        basename = os.path.basename(file)
        task_id, ext = basename.split('.')
        if task_id in delete_tgt_list:
            file = os.path.join(dir_tgt_path, file)  
            os.remove(file)

    default_host = '0.0.0.0'
    default_port = '5000'
    deafault_max_threads = '5'

    parser = ArgumentParser()

    parser.add_argument(
        "-ht", "--host", dest="host", default=default_host,
        help=f'Enter connect host; default="{default_host}"'
    )
    parser.add_argument(
        "-p", "--port", dest="port", default=default_port,
        help=f'Enter connect port; default="{default_port}"'
    )
    parser.add_argument(
        "-t", "--threads", dest="threads", default=deafault_max_threads,
        help=f'Enter max threads; default="{deafault_max_threads}"'
    )

    args = parser.parse_args()
    os.environ["TRANSFORMERS_OFFLINE"] = "1"

    # Temp solution; neen use class--------
    os.environ['MAX_THREADS'] = args.threads 
    from api.tools.manager import Manager
    manager = Manager()
    # -------------------------------------

    app.run(
        host = args.host,
        port = args.port,
#        debug = True
    )





