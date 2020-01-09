from flask import Flask, request
import os

from wsdcalculator.calculatewsd import WSDCalculator
from wsdcalculator.processenvironment import get_environment_percentile
# from wsdcalculator.storage.sqlstorage import SQLStorage
from wsdcalculator.storage.memorystorage import MemoryStorage
from wsdcalculator.authentication.jwtauthenticator import JWTAuthenticator

import logging
from log.setup import setup_logger

setup_logger()
logger = logging.getLogger(__name__)
app = Flask(__name__)

# storage = SQLStorage()
storage = MemoryStorage()
calculator = WSDCalculator(storage)
authenticator = JWTAuthenticator()

@app.route('/evaluation', methods=['POST'])
def create_evaluation():
    logger.info('[event=create-evaluation][remoteAddress=%s]', request.remote_addr)
    user = authenticator.get_user(request.headers[authenticator.header_key])

    f = request.files['recording']
    threshold = get_environment_percentile(f)
    id = storage.create_evaluation(threshold, user)
    result = {
        'evaluationId': id
    }
    return result

@app.route('/evaluation/<evaluationId>', methods=['GET'])
def get_evaluation(evaluationId):
    logger.info('[event=get-evaluation][evaluationId=%s][remoteAddress=%s]', evaluationId, request.remote_addr)
    user = authenticator.get_user(request.headers[authenticator.header_key])
    
    attempts = storage.fetch_attempts(evaluationId, user)
    result = {
        'attempts': [a.__dict__ for a in attempts]
    }
    return result

@app.route('/evaluation/<evaluationId>/attempt', methods=['POST'])
def process_attempt(evaluationId):
    logger.info('[event=create-attempt][evaluationId=%s][remoteAddress=%s]', evaluationId, request.remote_addr)
    user = authenticator.get_user(request.headers[authenticator.header_key])

    f = request.files['recording']
    syllable_count = request.args.get('syllableCount')
    syllable_count = int(syllable_count)
    term = request.args.get('word')
    if syllable_count is None:
        return 'Must provide syllable count.'
    if term is None:
        return 'Must provide attempted word.'

    method = request.args.get('method')
    if method is None or method == '':
        method = 'average'
    wsd, duration = calculator.calculate_wsd(f, syllable_count, evaluationId, method)
    id = storage.create_attempt(evaluationId, term, wsd, duration, user)
    result = {
        'attemptId': id,
        'wsd': wsd
    }
    return result

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)

@app.route('/evaluation/<evaluationId>/attempt/<attemptId>/recording', methods=['POST', 'GET'])
def save_recording(evaluationId, attemptId):
    if request.method == 'POST':
        logger.info('[event=save-recording][evaluationId=%s][attemptId=%s][remoteAddress=%s]', evaluationId, attemptId, request.remote_addr)
        user = authenticator.get_user(request.headers[authenticator.header_key])

        f = request.files['recording']
        id = storage.save_recording(f, evaluationId, attemptId, user)
        result = {
            'attemptId': id
        }
    else:
        logger.info('[event=get-recording][evaluationId=%s][attemptId=%s][remoteAddress=%s]', evaluationId, attemptId, request.remote_addr)
        user = authenticator.get_user(request.headers[authenticator.header_key])

        f = storage.get_recording(evaluationId, attemptId, user)
        result = f
    return result