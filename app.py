from flask import Flask, request, jsonify, send_file

from src import ApraxiatorException
from src.authentication.authprovider import get_auth

from src.controllers import DataExportController, EvaluationController, WaiverController
from src.services import DataExportService, EvaluationService, WaiverService
from src.storage.dbexceptions import ConnectionException
from src.utils import EmailSender, PDFGenerator


import logging
from log.setup import setup_logger

setup_logger()
logger = logging.getLogger(__name__)
app = Flask(__name__)

try:
    from src.storage.sqlstorage import SQLStorage
    storage = SQLStorage()
except ConnectionException as e:
    logger.exception('Problem establishing SQL connection')
    from src.storage.memorystorage import MemoryStorage
    storage = MemoryStorage()

email_sender = EmailSender()
pdf_generator = PDFGenerator()
export_controller = DataExportController(DataExportService(storage))
evaluation_controller = EvaluationController(EvaluationService(storage, email_sender, pdf_generator))
waiver_controller = WaiverController(WaiverService(storage, email_sender, pdf_generator))

authenticator = get_auth()


@app.before_request
def log_access():
    logger.info(f'[event=endpoint-call][endpoint={request.endpoint}][remoteAddress={request.remote_addr}]')


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
        logger.error('[event=returning-notimplementederror][error=%r]', error)
        return form_result({'errorMessage': 'Sorry, that request cannot be completed'}, 418)
    else:
        logger.error('[event=returning-unknown-error][error=%s]', error)
        return form_result({'errorMessage': 'An unknown error occurred.'}, 500)


@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    storage.is_healthy()
    result = {
        'message': 'all is well'
    }
    return form_result(result)


@app.route('/evaluation', methods=['GET'])
def list_evaluations():
    token = authenticator.get_token(request.headers)
    user = authenticator.get_user(token)
    result = evaluation_controller.handle_list_evaluations(request, user)
    return form_result(result)


@app.route('/evaluation', methods=['POST'])
def create_evaluation():
    token = authenticator.get_token(request.headers)
    user = authenticator.get_user(token)
    result = evaluation_controller.handle_create_evaluation(request, user)
    return form_result(result)


@app.route('/evaluation/<evaluation_id>/ambiance', methods=['POST'])
def add_ambiance(evaluation_id):
    token = authenticator.get_token(request.headers)
    user = authenticator.get_user(token)
    result = evaluation_controller.handle_add_ambiance(request, user, evaluation_id)
    return form_result(result)


@app.route('/evaluation/<evaluation_id>/attempts', methods=['GET'])
def get_attempts(evaluation_id):
    token = authenticator.get_token(request.headers)
    user = authenticator.get_user(token)
    result = evaluation_controller.handle_get_attempts(request, user, evaluation_id)
    return form_result(result)


@app.route('/evaluation/<evaluation_id>/attempt', methods=['POST'])
def process_attempt(evaluation_id):
    token = authenticator.get_token(request.headers)
    user = authenticator.get_user(token)
    result = evaluation_controller.handle_create_attempt(request, user, evaluation_id)
    return form_result(result)


@app.route('/evaluation/<evaluation_id>/attempt/<attempt_id>', methods=['PUT'])
def update_attempt(evaluation_id, attempt_id):
    token = authenticator.get_token(request.headers)
    user = authenticator.get_user(token)
    result = evaluation_controller.handle_update_attempt(request, user, evaluation_id, attempt_id)
    return form_result(result)


@app.route('/waiver', methods=['GET'])
def check_waivers():
    token = authenticator.get_token(request.headers)
    user = authenticator.get_user(token)
    result = waiver_controller.handle_check_waivers(request, user)
    return form_result(result)


@app.route('/waiver/subject', methods=['POST'])
def save_subject_waiver():
    token = authenticator.get_token(request.headers)
    user = authenticator.get_user(token)
    result = waiver_controller.handle_save_subject_waiver(request, user)
    return form_result(result)


@app.route('/waiver/representative', methods=['POST'])
def save_representative_waiver():
    token = authenticator.get_token(request.headers)
    user = authenticator.get_user(token)
    result = waiver_controller.handle_save_representative_waiver(request, user)
    return form_result(result)


@app.route('/waiver/<waiver_id>/invalidate', methods=['PUT'])
def invalidate_waiver(waiver_id):
    token = authenticator.get_token(request.headers)
    user = authenticator.get_user(token)
    result = waiver_controller.handle_invalidate_waiver(request, user, waiver_id)
    return form_result(result)


@app.route('/export', methods=['POST'])
def export():
    token = authenticator.get_token(request.headers)
    user = authenticator.get_user(token)
    export_file = export_controller.handle_export(request, user)
    return send_file(export_file)


@app.route('/sendReport/<evaluation_id>', methods=['POST'])
def send_report(evaluation_id):
    token = authenticator.get_token(request.headers)
    user = authenticator.get_user(token)
    result = evaluation_controller.handle_send_report(request, user, evaluation_id)
    return form_result(result)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080, ssl_context=('cert.pem', 'key.pem'))
