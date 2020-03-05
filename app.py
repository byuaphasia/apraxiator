import os
from flask import Flask, request, jsonify, send_file

from src import ApraxiatorException, InvalidRequestException
from src.authentication.authprovider import get_auth

from src.waiver.waiver_sender import WaiverSender
from src.waiver.waiver_generator import WaiverGenerator
from src.models.waiver import Waiver
from src.storage.storageexceptions import WaiverAlreadyExists
from src.controllers import DataExportController, EvaluationController
from src.services import DataExportService, EvaluationService
from src.report.report_sender import ReportSender
from src.report.report_generator import ReportGenerator
from src.storage.dbexceptions import ConnectionException


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

export_controller = DataExportController(DataExportService(storage))
evaluation_controller = EvaluationController(EvaluationService(storage))

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


@app.route('/waiver/<signer>', methods=['POST'])
def save_waiver(signer):
    token = authenticator.get_token(request.headers)
    user = authenticator.get_user(token)
    logger.info('[event=save-waiver][user=%s][signer=%s][remoteAddress=%s]', user, signer, request.remote_addr)

    generator = WaiverGenerator()
    res_name = request.values.get('researchSubjectName')
    res_email = request.values.get('researchSubjectEmail')
    clinician_email = request.values.get('clinicianEmail')
    rep_name = ''
    rep_relationship = ''
    if signer == 'subject':
        res_file = request.files['researchSubjectSignature']
        date = request.values.get('researchSubjectDate')
        report_file = generator.create_pdf_report(res_name, res_email, date, res_file, rep_name, rep_relationship, '', None)
    elif signer == 'representative':
        rep_file = request.files['representativeSignature']
        rep_name = request.values.get('representativeName')
        rep_relationship = request.values.get('representativeRelationship')
        date = request.values.get('representativeDate')
        report_file = generator.create_pdf_report(
            res_name, res_email, '', None, rep_name, rep_relationship, date, rep_file
        )
    else:
        raise InvalidRequestException('Invalid signer. Must be \'subject\' or \'representative\'.')
    
    waiver = Waiver(res_name, res_email, date, report_file, signer, True, rep_name, rep_relationship, None, user)
    try:
        storage.add_waiver(waiver)
    except WaiverAlreadyExists:
        logger.info('[event=waiver-exists][resName=%s][resEmail=%s][remoteAddress=%s]', res_name, res_email, request.remote_addr)
        result = {
            'message': 'Waiver for this user already exists.'
        }
        return form_result(result)

    logger.info('[event=report-generated][user=%s][signer=%s][remoteAddress=%s]', user, signer, request.remote_addr)
    WaiverSender.send_patient_email(report_file, res_email)
    WaiverSender.send_clinician_email(report_file, clinician_email, res_name)
    logger.info('[event=report-sent][user=%s][destination=%s][remoteAddress=%s]', user, res_email, request.remote_addr)
    return form_result({})


@app.route('/waiver/<res_name>/<res_email>', methods=['GET'])
def check_waivers(res_name, res_email):
    token = authenticator.get_token(request.headers)
    user = authenticator.get_user(token)
    logger.info('[event=get-waivers][user=%s][remoteAddress=%s]', user, request.remote_addr)
    if res_name is None or res_email is None:
        return InvalidRequestException('Must provide both a name and email address')
    waivers = storage.get_valid_waivers(res_name, res_email, user)
    result = {
        'waivers': [w.to_response() for w in waivers]
    }
    return form_result(result)


@app.route('/invalidate/waiver/<res_name>/<res_email>', methods=['PUT'])
def invalidate_waiver(res_name, res_email):
    token = authenticator.get_token(request.headers)
    user = authenticator.get_user(token)
    logger.info('[event=invalidate-waiver][user=%s][remoteAddress=%s]', user, request.remote_addr)
    if res_name is None or res_email is None:
        return InvalidRequestException('Must provide both a name and email address')
    storage.invalidate_waiver(res_name, res_email, user)
    return form_result({})


@app.route('/export', methods=['POST'])
def export():
    token = authenticator.get_token(request.headers)
    user = authenticator.get_user(token)
    export_file = export_controller.handle_export(request, user)
    return send_file(export_file)


@app.route('/sendReport', methods=['POST'])
def send_report():
    token = authenticator.get_token(request.headers)
    user = authenticator.get_user(token)
    eval_id = request.values.get('evalId')
    email = request.values.get('email')
    if email is None or eval_id is None:
        return InvalidRequestException('Must provide both an email address and evaluation ID')
    logger.info('[event=send-report][user=%s][remoteAddress=%s][evalId=%s]', user, request.remote_addr, eval_id)
    name = request.values.get('name')
    eval_report = evaluation_controller.handle_get_evaluation_report(request, user, eval_id)
    sum_wsd = 0
    for attempt in eval_report['attempts']:
        sum_wsd += attempt['wsd']
        attempt['wsd'] = '{0:.2f}'.format(attempt['wsd'])
    avg_wsd = sum_wsd / len(eval_report['attempts'])
    report_generator = ReportGenerator()
    report_file = report_generator.create_pdf_report(eval_id, eval_report['date'], name, eval_report['attempts'], avg_wsd, eval_report['gender'], eval_report['age'], eval_report['impression'])
    ReportSender.send_report_email(report_file, email, eval_id)
    if os.path.isfile(report_file):
        os.remove(report_file)
    return form_result({})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080, ssl_context=('cert.pem', 'key.pem'))
