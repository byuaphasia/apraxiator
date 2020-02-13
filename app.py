from flask import Flask, request, jsonify, send_file
import io

from wsdcalculator import WSDCalculator, ApraxiatorException, InvalidRequestException, get_ambiance_threshold
from wsdcalculator.authentication.authprovider import get_auth

from wsdcalculator.waiver.waiver_sender import WaiverSender
from wsdcalculator.waiver.waiver_generator import WaiverGenerator
from wsdcalculator.models.waiver import Waiver
from wsdcalculator.storage.storageexceptions import WaiverAlreadyExists

import logging
from log.setup import setup_logger

setup_logger()
logger = logging.getLogger(__name__)
app = Flask(__name__)

try:
  from wsdcalculator.storage.sqlstorage import SQLStorage
  storage = SQLStorage()
except Exception as e:
  logger.exception('Problem establishing SQL connection')
  from wsdcalculator.storage.memorystorage import MemoryStorage
  storage = MemoryStorage()

calculator = WSDCalculator(storage)
authenticator = get_auth()

def form_result(content, code=200):
    result = jsonify(content)
    result.status_code = code
    return result

@app.errorhandler(Exception)
def handle_failure(error: Exception):
    if isinstance(error, ApraxiatorException):
        logger.error('[event=returning-error][errorMessage=%s][errorCode=%s]', error.get_message(), error.get_code())
        return form_result(error.to_response(), error.get_code())
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
    logger.info('[event=list-evaluations][user=%s][remoteAddress=%s]', user, request.remote_addr)

    evaluations = storage.list_evaluations(user)
    result = {
        'evaluations': [e.to_list_response() for e in evaluations]
    }
    return form_result(result)

@app.route('/evaluation', methods=['POST'])
def create_evaluation():
    token = authenticator.get_token(request.headers)
    user = authenticator.get_user(token)
    logger.info('[event=create-evaluation][user=%s][remoteAddress=%s]', user, request.remote_addr)

    content = request.json
    try:
        age = content['age']
        gender = content['gender']
        impression = content['impression']
    except KeyError as e:
        msg = f'Must provide {e.args[0]}'
        raise InvalidRequestException(msg, e)
    storage.create_evaluation(age, gender, impression, user)

@app.route('/evaluation/<evaluationId>/ambiance', methods=['POST'])
def add_ambiance(evaluationId):
    token = authenticator.get_token(request.headers)
    user = authenticator.get_user(token)
    logger.info('[event=add-ambiance][user=%s][evaluationId=%s][remoteAddress=%s]', user, evaluationId, request.remote_addr)

    f = request.files['recording']
    if f is None:
        raise InvalidRequestException('Must attach a file called "recording"')
    threshold = get_ambiance_threshold(f)

    storage.add_threshold(evaluationId, threshold, user)
    return form_result({})

@app.route('/evaluation/<evaluationId>/attempts', methods=['GET'])
def get_attempts(evaluationId):
    token = authenticator.get_token(request.headers)
    user = authenticator.get_user(token)
    logger.info('[event=get-attempts][user=%s][evaluationId=%s][remoteAddress=%s]', user, evaluationId, request.remote_addr)

    attempts = storage.fetch_attempts(evaluationId, user)
    result = {
        'attempts': [a.to_response() for a in attempts]
    }
    return form_result(result)

@app.route('/evaluation/<evaluationId>/attempt', methods=['POST'])
def process_attempt(evaluationId):
    token = authenticator.get_token(request.headers)
    user = authenticator.get_user(token)
    logger.info('[event=create-attempt][user=%s][evaluationId=%s][remoteAddress=%s]', user, evaluationId, request.remote_addr)

    f = request.files['recording']
    syllable_count = request.values.get('syllableCount')
    syllable_count = int(syllable_count)
    word = request.values.get('word')
    if syllable_count is None:
        raise InvalidRequestException('Must provide syllable count')
    elif syllable_count <= 0:
        raise InvalidRequestException('Syllable count was {}, must be greater than 0'.format(syllable_count))
    if word is None or word == '':
        raise InvalidRequestException('Must provide attempted word')

    method = request.values.get('method')
    if method is None or method == '':
        method = 'average'
    wsd, duration = calculator.calculate_wsd(f, syllable_count, evaluationId, user, method)
    id = storage.create_attempt(evaluationId, word, wsd, duration, user)
    result = {
        'attemptId': id,
        'wsd': wsd
    }
    return form_result(result)

@app.route('/evaluation/<evaluationId>/attempt/<attemptId>/recording', methods=['POST', 'GET'])
def save_recording(evaluationId, attemptId):
    token = authenticator.get_token(request.headers)
    user = authenticator.get_user(token)
    if request.method == 'POST':
        logger.info('[event=save-recording][user=%s][evaluationId=%s][attemptId=%s][remoteAddress=%s]', user, evaluationId, attemptId, request.remote_addr)
        f = request.files['recording'].read()
        storage.save_recording(f, evaluationId, attemptId, user)
        return form_result({})
    else:
        logger.info('[event=get-recording][user=%s][evaluationId=%s][attemptId=%s][remoteAddress=%s]', user, evaluationId, attemptId, request.remote_addr)
        f = storage.get_recording(evaluationId, attemptId, user)
        return send_file(io.BytesIO(f), mimetype='audio/wav')


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
    
    waiver = Waiver(res_name, res_email, date, report_file, signer, True, rep_name, rep_relationship)
    try:
        storage.add_waiver(waiver)
    except WaiverAlreadyExists:
        logger.info('[event=waiver-exists][resName=%s][resEmail=%s][remoteAddress=%s]', res_name, res_email, request.remote_addr)
        result = {
            'message': 'Waiver for this user already exists.'
        }
        return form_result(result)

    logger.info('[event=report-generated][user=%s][signer=%s][remoteAddress=%s]', user, signer, request.remote_addr)
    sender = WaiverSender()
    sender.send_patient_waiver(report_file, res_email)
    sender.send_clinician_email(report_file, clinician_email, res_name)
    logger.info('[event=report-sent][user=%s][destination=%s][remoteAddress=%s]', user, res_email, request.remote_addr)
    return form_result({})


@app.route('/waiver/<res_name>/<res_email>', methods=['GET'])
def check_waivers(res_name, res_email):
    token = authenticator.get_token(request.headers)
    user = authenticator.get_user(token)
    logger.info('[event=get-waivers][user=%s][remoteAddress=%s]', user, request.remote_addr)
    if res_name is None or res_email is None:
        return InvalidRequestException('Must provide both a name and email address')
    waivers = storage.get_valid_waivers(res_name, res_email)
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
    storage.invalidate_waiver(res_name, res_email)
    return form_result({})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080, ssl_context=('cert.pem', 'key.pem'))
