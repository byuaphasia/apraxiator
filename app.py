from flask import Flask, request, jsonify, send_file
import os
import io

from wsdcalculator.calculatewsd import WSDCalculator
from wsdcalculator.processenvironment import get_environment_percentile
from wsdcalculator.authentication.jwtauthenticator import JWTAuthenticator, get_token
from wsdcalculator.apraxiatorexception import ApraxiatorException, InvalidRequestException

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
authenticator = JWTAuthenticator()

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
    token = get_token(request.headers)
    user = authenticator.get_user(token)
    logger.info('[event=create-evaluation][user=%s][remoteAddress=%s]', user, request.remote_addr)

    f = request.files['recording']
    threshold = get_environment_percentile(f)
    id = storage.create_evaluation(threshold, user)
    result = {
        'evaluationId': id
    }
    logger.info('evaluation created')
    return jsonify(result)

@app.route('/evaluation/<evaluationId>', methods=['GET'])
def get_evaluation(evaluationId):
    token = get_token(request.headers)
    user = authenticator.get_user(token)
    logger.info('[event=get-evaluation][user=%s][evaluationId=%s][remoteAddress=%s]', user, evaluationId, request.remote_addr)

    attempts = storage.fetch_attempts(evaluationId, user)
    result = {
        'attempts': [a.__dict__ for a in attempts]
    }
    return jsonify(result)

@app.route('/evaluation/<evaluationId>/attempt', methods=['POST'])
def process_attempt(evaluationId):
    token = get_token(request.headers)
    user = authenticator.get_user(token)
    logger.info('[event=create-attempt][user=%s][evaluationId=%s][remoteAddress=%s]', user, evaluationId, request.remote_addr)

    f = request.files['recording']
    syllable_count = request.args.get('syllableCount')
    syllable_count = int(syllable_count)
    term = request.args.get('word')
    if syllable_count is None:
        raise InvalidRequestException('Must provide syllable count')
    if term is None:
        raise InvalidRequestException('Must provide attempted word')

    method = request.args.get('method')
    if method is None or method == '':
        method = 'average'
    wsd, duration = calculator.calculate_wsd(f, syllable_count, evaluationId, method)
    id = storage.create_attempt(evaluationId, term, wsd, duration, user)
    result = {
        'attemptId': id,
        'wsd': wsd
    }
    return jsonify(result)

@app.route('/evaluation/<evaluationId>/attempt/<attemptId>/recording', methods=['POST', 'GET'])
def save_recording(evaluationId, attemptId):
    token = get_token(request.headers)
    user = authenticator.get_user(token)
    if request.method == 'POST':
        logger.info('[event=save-recording][user=%s][evaluationId=%s][attemptId=%s][remoteAddress=%s]', user, evaluationId, attemptId, request.remote_addr)
        f = request.files['recording'].read()
        id = storage.save_recording(f, evaluationId, attemptId, user)
        result = {
            'attemptId': id
        }
        result = jsonify(result)
        return result
    else:
        logger.info('[event=get-recording][user=%s][evaluationId=%s][attemptId=%s][remoteAddress=%s]', user, evaluationId, attemptId, request.remote_addr)
        f = storage.get_recording(evaluationId, attemptId, user)
        return send_file(io.BytesIO(f), mimetype='audio/wav')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080, ssl_context=('cert.pem', 'key.pem'))
