from flask import Flask, request, jsonify, send_file
import os
import io

from wsdcalculator.calculatewsd import WSDCalculator
from wsdcalculator.processenvironment import get_environment_percentile
from wsdcalculator.storage.sqlstorage import SQLStorage
# from wsdcalculator.storage.memorystorage import MemoryStorage

import logging
from log.setup import setup_logger

setup_logger()
logger = logging.getLogger(__name__)
app = Flask(__name__)

storage = SQLStorage()
# storage = MemoryStorage()
calculator = WSDCalculator(storage)

@app.route('/evaluation', methods=['POST'])
def create_evaluation():
    logger.info('[event=create-evaluation][remoteAddress=%s]', request.remote_addr)

    f = request.files['recording'].read()
    threshold = get_environment_percentile(f)
    id = storage.create_evaluation(threshold, '')
    result = {
        'evaluationId': id
    }
    logger.info('evaluation created')
    return jsonify(result)

@app.route('/evaluation/<evaluationId>', methods=['GET'])
def get_evaluation(evaluationId):
    logger.info('[event=get-evaluation][evaluationId=%s][remoteAddress=%s]', evaluationId, request.remote_addr)
    
    attempts = storage.fetch_attempts(evaluationId, '')
    result = {
        'attempts': [a.__dict__ for a in attempts]
    }
    return jsonify(result)

@app.route('/evaluation/<evaluationId>/attempt', methods=['POST'])
def process_attempt(evaluationId):
    logger.info('[event=create-attempt][evaluationId=%s][remoteAddress=%s]', evaluationId, request.remote_addr)

    f = request.files['recording'].read()
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
    id = storage.create_attempt(evaluationId, term, wsd, duration, '')
    result = {
        'attemptId': id,
        'wsd': wsd
    }
    return jsonify(result)

@app.route('/evaluation/<evaluationId>/attempt/<attemptId>/recording', methods=['POST', 'GET'])
def save_recording(evaluationId, attemptId):
    if request.method == 'POST':
        logger.info('[event=save-recording][evaluationId=%s][attemptId=%s][remoteAddress=%s]', evaluationId, attemptId, request.remote_addr)

        f = request.files['recording'].read()
        print(type(f))
        id = storage.save_recording(f, evaluationId, attemptId, '')
        result = {
            'attemptId': id
        }
        result = jsonify(result)
        return result
    else:
        logger.info('[event=get-recording][evaluationId=%s][attemptId=%s][remoteAddress=%s]', evaluationId, attemptId, request.remote_addr)

        f = storage.get_recording(evaluationId, attemptId, '')
        return send_file(io.BytesIO(f), mimetype='audio/wav')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)