import os
import sys
from pathlib import Path
from flask import Flask
from flask_restx import Resource, Api, fields
from flask_cors import CORS, cross_origin
from werkzeug.datastructures import FileStorage
from random import randint, choice
from api.recognitions import recognize
from time import time
from datetime import timedelta
from api.tools.manager import Manager


# Local path settings
drive, path_and_file = os.path.splitdrive(Path(__file__).absolute())
path, file = os.path.split(path_and_file)
curdir = os.path.join(drive, path)

app = Flask(__name__)
api = Api(
    app, 
    version='1.0',
    title='ASR',
    description='ASR',
    doc="/api",
)

CORS(app)
namespace = api.namespace('api', description='ASR_cors?')

start_response = api.model('StartResponse', {
    'task_id': fields.String
})


task_info = api.model('TaskInfo', {
    'id': fields.String
})


result_response = api.model('ResultResponse', {
    'result': fields.String
})


alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
get_file_prefix = lambda: ''.join(choice(alphabet) for _ in range(32))

upload_parser = api.parser()
upload_parser.add_argument('file', location='files',
                            type=FileStorage, required=True
                          )
manager = Manager()

@api.route('/one_video')
@api.expect(upload_parser)
class Upload(Resource):
    def post(self):
        times = {
            'start': None,
            'get_prefix': None,
            'uploaded_file': None,
            'recognize': None,
        }
        args = upload_parser.parse_args()
        uploaded_file = args['file']  # This is FileStorage instance
        times['start'] = time()
        file_prefix = get_file_prefix()
        times['get_prefix'] = time()
        dir_local_path = os.path.join(curdir, 'api', 'tempfiles', 'src') 
        file_local_path = os.path.join(
            dir_local_path,  
            f'{file_prefix}_{uploaded_file.filename}'
        )
        uploaded_file.save(file_local_path)
        times['uploaded_file'] = time()  
        text = recognize(file_local_path)
        times['recognize'] = time()  

        response = {
            'message': recognize(file_local_path),
            'get_prefix': str(timedelta(seconds = times['get_prefix'] - times['start'])),
            'uploaded_file': str(timedelta(seconds = times['uploaded_file'] - times['get_prefix'])),
            'recognize': str(timedelta(seconds = times['recognize'] - times['uploaded_file'])),
            'full': str(timedelta(seconds = times['recognize'] - times['start'])),
        } 
        return response, 200



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
    @namespace.doc('ProcessedSubtitles')
    @namespace.expect(task_info)
    @namespace.marshal_with(result_response, code=200)
    def post(self):
        data = api.payload
        task_id = data['id']
        result = manager.get_results(task_id=task_id)
        return {'result': result}, 200




if __name__ == '__main__':
    app.run(debug=True)




