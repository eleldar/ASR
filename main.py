import os
import sys
from pathlib import Path
from flask import Flask
from flask_restx import Resource, Api
from werkzeug.datastructures import FileStorage
from random import randint, choice
from api.recognitions import recognize

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
alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
get_file_prefix = lambda: ''.join(choice(alphabet) for _ in range(32))

upload_parser = api.parser()
upload_parser.add_argument('file', location='files',
                            type=FileStorage, required=True
                          )

@api.route('/one_video')
@api.expect(upload_parser)
class Upload(Resource):
    def post(self):
        args = upload_parser.parse_args()
        uploaded_file = args['file']  # This is FileStorage instance
        file_prefix = get_file_prefix()
        dir_local_path = os.path.join(curdir, 'api', 'tempfiles', 'src') 
        file_local_path = os.path.join(
            dir_local_path,  
            f'{file_prefix}_{uploaded_file.filename}'
        )
        uploaded_file.save(file_local_path)
        return {'message': recognize(file_local_path)}, 200


if __name__ == '__main__':
    app.run(debug=True)




