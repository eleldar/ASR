import werkzeug
import numpy as np
from flask import Flask, request, make_response
from flask_cors import CORS, cross_origin
from flask_restx import Api, Resource, fields, marshal, reqparse

from src.manager import Manager

image_upload = reqparse.RequestParser()
image_upload.add_argument('file',
                          type=werkzeug.datastructures.FileStorage,
                          location='files',
                          required=True,
                          help='Видеофайл не может быть пустым.')

manager = Manager()


def create_app():
    app = Flask('edges')
    app.config['RESTPLUS_MASK_SWAGGER'] = False  # Enable or disable the mask field, by default X-Fields

    api = Api(app, version='1.0', title='SRT Extraction API',
              description='Сервис извлекает строку в SRT формате из видео с субтитрами.\n '
                          'Операция извлечение выполняется в два этапа:\n'
                          'Сначала вам нужно загрузить видео в формате mp4 (для этого откройте api/start и нажмите '
                          '"try it out", затем выберите соответствующий файл). Метод "start" вернет случайный id.\n'
                          'Далее вставьте этот id в task_id по адресу api/progress. '
                          'Отклик будет сожержать информацию о текущем прогрессе (в процентах)\n'
                          ' и текущий статуст ошибки, если она возникла в ходе обработки видеофайла.'
                          ' Если вы хотите скачать уже обработанные субтитры, '
                          'повторите описанные выше действия в разделе "api/result"\n\n'
                          'Файл с субтитрами представлен в формате json. Для ковертации в vtt/txt, '
                          'используйте вспомогательный скрипт "str_to_txt-vtt.py"'
              )

    CORS(app)
    namespace = api.namespace('api', description=' AllApis:\n start - convert video to srt like string \n'
                                                 'progress - get process status by unique id \n'
                                                 'result - obtain and download cultivated subtitles '
                                                 'in srt-like structure\n'
                                                 'tasks - gain current add previous tasks')

    start_response = api.model('StartResponse', {
        'task_id': fields.Integer
    })

    progress_response = api.model('ProgressResponse', {
        'error': fields.String,
        'current_progress': fields.String,
    })

    result_response = api.model('ResultResponse', {
        'result': fields.String
    })

    tasks_response = api.model('TasksResponse', {
        'task_list': fields.List(fields.Integer)
    })

    task_info = api.model('TaskInfo', {
        'id': fields.Integer
    })

    def convert_data_to_vtt(json_data):
        """
        :param json_data: some data in json format
        :return: text from subtitles in vtt format
        """
        print(json_data)
        df = 'WEBVTT\n\n' + json_data['result']
        # add some code may be? Or it's enough
        return df

    @api.representation('application/vtt')
    def vtt(data, code, headers=None):
        resp = make_response(convert_data_to_vtt(data), code)
        resp.headers.extend(headers or {})
        return resp


    @namespace.route('/start')
    class DetectApi(Resource):
        @namespace.doc('VideoHandleStart')
        @namespace.expect(image_upload)
        @namespace.marshal_with(start_response, code=201)
        def post(self):
            args = image_upload.parse_args()
            file = args['file']

            task_id = manager.start(file)

            return {'task_id': task_id}, 201

    @namespace.route('/progress')
    class DetectApi(Resource):
        @namespace.doc('VideoHandleProgress')
        @namespace.expect(task_info)
        @namespace.marshal_with(progress_response, code=200)
        def post(self):
            data = api.payload
            task_id = data['id']
            error, current_frame, num_frames = manager.get_status(task_id=task_id)
            return {
                'error': error,
                'current_progress': str(np.round(current_frame/num_frames, 3) * 100)[0:4] + '%',
            }, 200

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

    @namespace.route('/tasks')
    class DetectApi(Resource):
        @namespace.doc('AllTaskIDs')
        @namespace.marshal_with(tasks_response, code=200)
        def get(self):
            tasks_ids = manager.get_tasks()
            return {'task_list': tasks_ids}, 200

    return app


if __name__ == '__main__':
    create_app().run(port=5005, debug=False, host='0.0.0.0')
