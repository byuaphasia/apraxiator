from flask import Flask, request, jsonify, send_file
import os
import io

from wsdcalculator.calculatewsd import WSDCalculator
from wsdcalculator.processenvironment import get_environment_percentile
from wsdcalculator.authentication.authprovider import get_auth
from wsdcalculator.apraxiatorexception import ApraxiatorException, InvalidRequestException

from waiver.waiver_sender import WaiverSender
from waiver.waiver_generator import WaiverGenerator

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

@app.errorhandler(ApraxiatorException)
def handle_failure(error: ApraxiatorException):
    result = jsonify(error.to_dict())
    result.status_code = error.get_code()
    return result

@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    storage.is_healthy()
    result = {
        'message': 'all is well'
    }
    return jsonify(result)

@app.route('/evaluation', methods=['POST'])
def create_evaluation():
    token = authenticator.get_token(request.headers)
    user = authenticator.get_user(token)
    logger.info('[event=create-evaluation][user=%s][remoteAddress=%s]', user, request.remote_addr)

    f = request.files['recording']
    threshold = get_environment_percentile(f)
    id = storage.create_evaluation(threshold, user)
    result = {
        'evaluationId': id
    }
    return jsonify(result)

@app.route('/evaluation/<evaluationId>', methods=['GET'])
def get_evaluation(evaluationId):
    token = authenticator.get_token(request.headers)
    user = authenticator.get_user(token)
    logger.info('[event=get-evaluation][user=%s][evaluationId=%s][remoteAddress=%s]', user, evaluationId, request.remote_addr)

    attempts = storage.fetch_attempts(evaluationId, user)
    result = {
        'attempts': [a.to_dict() for a in attempts]
    }
    return jsonify(result)

@app.route('/evaluation/<evaluationId>/attempt', methods=['POST'])
def process_attempt(evaluationId):
    token = authenticator.get_token(request.headers)
    user = authenticator.get_user(token)
    logger.info('[event=create-attempt][user=%s][evaluationId=%s][remoteAddress=%s]', user, evaluationId, request.remote_addr)

    f = request.files['recording']
    syllable_count = request.args.get('syllableCount')
    syllable_count = int(syllable_count)
    word = request.args.get('word')
    if syllable_count is None:
        raise InvalidRequestException('Must provide syllable count')
    elif syllable_count <= 0:
        raise InvalidRequestException('Syllable count was {}, must be greater than 0'.format(syllable_count))
    if word is None or word == '':
        raise InvalidRequestException('Must provide attempted word')

    method = request.args.get('method')
    if method is None or method == '':
        method = 'average'
    wsd, duration = calculator.calculate_wsd(f, syllable_count, evaluationId, user, method)
    id = storage.create_attempt(evaluationId, word, wsd, duration, user)
    result = {
        'attemptId': id,
        'wsd': wsd
    }
    return jsonify(result)

@app.route('/evaluation/<evaluationId>/attempt/<attemptId>/recording', methods=['POST', 'GET'])
def save_recording(evaluationId, attemptId):
    token = authenticator.get_token(request.headers)
    user = authenticator.get_user(token)
    if request.method == 'POST':
        logger.info('[event=save-recording][user=%s][evaluationId=%s][attemptId=%s][remoteAddress=%s]', user, evaluationId, attemptId, request.remote_addr)
        f = request.files['recording'].read()
        storage.save_recording(f, evaluationId, attemptId, user)
        result = {}
        result = jsonify(result)
        return result
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
    if signer == 'subject':
        res_file = request.files['researchSubjectSignature']
        res_date = request.values.get('researchSubjectDate')
        report_file = generator.create_pdf_report(res_name, res_email, res_file, res_date, '', '', '', None)
    elif signer == 'representative':
        rep_file = request.files['representativeSignature']
        rep_name = request.values.get('representativeName')
        rep_relationship = request.values.get('representativeRelationship')
        rep_date = request.values.get('representativeDate')
        report_file = generator.create_pdf_report(
            res_name, res_email, None, '', rep_name, rep_relationship, rep_date, rep_file
        )
    else:
        raise InvalidRequestException('Invalid signer. Must be \'subject\' or \'representative\'.')
#     TODO: save report in storage somewhere with other info
    logger.info('[event=report-generated][user=%s][signer=%s][remoteAddress=%s]', user, signer, request.remote_addr)
    sender = WaiverSender()
    sender.send_waiver(report_file, res_email)
    logger.info('[event=report-sent][user=%s][destination=%s][remoteAddress=%s]', user, res_email, request.remote_addr)
    result = {
        'message': 'Waiver successfully sent to %s'.format(res_email)
    }
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080, ssl_context=('cert.pem', 'key.pem'))
