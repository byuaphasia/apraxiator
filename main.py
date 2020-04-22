from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.exceptions import NotFound
import logging
import os

from src.apraxiatorexception import ApraxiatorException
from src.utils.factory import Factory
from src.utils.log import setup_logger

setup_logger()
logger = logging.getLogger(__name__)
app = Flask(__name__)
CORS(app)

factory = Factory.create_factory()
export_controller = factory.de_controller
evaluation_controller = factory.ev_controller
waiver_controller = factory.wv_controller


@app.before_request
def log_access():
    logger.info('[event=endpoint-call][endpoint=%s][remoteAddress=%s]', request.endpoint, request.remote_addr)


def form_result(content, code=200):
    result = jsonify(content)
    result.status_code = code
    log_msg = ''
    if hasattr(result, 'msg'):
        log_msg = result.msg
    logger.info('[event=form-response][code=%s][content=%s]', code, log_msg)
    return result


@app.errorhandler(Exception)
def handle_failure(error: Exception):
    if isinstance(error, ApraxiatorException):
        logger.error('[event=returning-error][errorMessage=%s][errorCode=%s]', error.get_message(), error.get_code())
        return form_result(error.to_response(), error.get_code())
    elif isinstance(error, NotImplementedError):
        logger.error('[event=returning-not-implemented][error=%r]', error)
        return form_result({'errorMessage': 'Sorry, that request cannot be completed'}, 418)
    elif isinstance(error, NotFound):
        logger.error('[event=returning-not-found][error=%r]', error)
        return error
    else:
        logger.error('[event=returning-unknown-error][type=%s][error=%s]', type(error), error)
        return form_result({'errorMessage': 'An unknown error occurred.'}, 500)


@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    factory.storage.is_healthy()
    result = {
        'message': 'all is well'
    }
    return form_result(result)


@app.route('/evaluation', methods=['GET'])
def list_evaluations():
    result = evaluation_controller.handle_list_evaluations(request)
    return form_result(result)


@app.route('/evaluation', methods=['POST'])
def create_evaluation():
    result = evaluation_controller.handle_create_evaluation(request)
    return form_result(result)


@app.route('/evaluation/<evaluation_id>/ambiance', methods=['POST'])
def add_ambiance(evaluation_id):
    result = evaluation_controller.handle_add_ambiance(request, evaluation_id=evaluation_id)
    return form_result(result)


@app.route('/evaluation/<evaluation_id>/attempts', methods=['GET'])
def get_attempts(evaluation_id):
    result = evaluation_controller.handle_get_attempts(request, evaluation_id=evaluation_id)
    return form_result(result)


@app.route('/evaluation/<evaluation_id>/attempt', methods=['POST'])
def process_attempt(evaluation_id):
    result = evaluation_controller.handle_create_attempt(request, evaluation_id=evaluation_id)
    return form_result(result)


@app.route('/evaluation/<evaluation_id>/attempt/<attempt_id>', methods=['PUT'])
def update_attempt(evaluation_id, attempt_id):
    result = evaluation_controller.handle_update_attempt(request, evaluation_id=evaluation_id, attempt_id=attempt_id)
    return form_result(result)


@app.route('/evaluation/<evaluation_id>/report', methods=['POST'])
def send_report(evaluation_id):
    result = evaluation_controller.handle_send_report(request, evaluation_id=evaluation_id)
    return form_result(result)


@app.route('/waiver', methods=['GET'])
def check_waivers():
    result = waiver_controller.handle_check_waivers(request)
    return form_result(result)


@app.route('/waiver/subject', methods=['POST'])
def save_subject_waiver():
    result = waiver_controller.handle_save_subject_waiver(request)
    return form_result(result)


@app.route('/export', methods=['POST'])
def export():
    export_file, filename = export_controller.handle_export(request)
    return send_file(export_file, attachment_filename=filename)


@app.route('/user', methods=['GET'])
def user():
    result = export_controller.handle_user(request)
    return form_result(result)


@app.route('/waiver/representative', methods=['POST'])
def save_representative_waiver():
    result = waiver_controller.handle_save_representative_waiver(request)
    return form_result(result)


@app.route('/waiver/<waiver_id>/invalidate', methods=['PUT'])
def invalidate_waiver(waiver_id):
    result = waiver_controller.handle_invalidate_waiver(request, waiver_id=waiver_id)
    return form_result(result)


if __name__ == '__main__':
    env = os.environ.get('APX_ENV', 'local')
    app.run(debug=True, host='0.0.0.0', port=8080, use_reloader=False)

