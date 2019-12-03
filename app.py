from flask import Flask, request
import os

from wsdcalculator.calculatewsd import WSDCalculator
from wsdcalculator.processenvironment import get_environment_percentile
from wsdcalculator.storage.sqlstorage import SQLStorage

app = Flask(__name__)

storage = SQLStorage()
calculator = WSDCalculator(storage)

@app.route('/evaluation', methods=['POST'])
def create_evaluation():
    f = request.files['recording']
    threshold = get_environment_percentile(f)
    id = storage.create_evaluation(threshold, '')
    result = {
        'evaluationId': id
    }
    return result

@app.route('/evaluation/<evaluationId>', methods=['GET'])
def get_evaluation(evaluationId):
    attempts = storage.fetch_attempts(evaluationId, '')
    result = {
        'attempts': [a.__dict__ for a in attempts]
    }
    return result

@app.route('/evaluation/<evaluationId>/attempt', methods=['POST'])
def process_attempt(evaluationId):
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
    id = storage.create_attempt(evaluationId, term, wsd, duration, '')
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
        f = request.files['recording']
        id = storage.save_recording(f, evaluationId, attemptId, '')
        result = {
            'attemptId': id
        }
    else:
        f = storage.get_recording(evaluationId, attemptId, '')
        result = f
    return result