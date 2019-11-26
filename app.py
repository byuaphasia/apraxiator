from flask import Flask, request
from werkzeug.utils import secure_filename
import os

from wsdcalculator.calculatewsd import WSDCalculator
from wsdcalculator.processenvironment import get_environment_percentile
from wsdcalculator.storage.memorystorage import MemoryStorage

app = Flask(__name__)

saved_files_dir = os.path.join(os.getcwd(), 'saved_files')
storage = MemoryStorage()
calculator = WSDCalculator(storage)

@app.route('/evaluation', methods=['POST'])
def create_evaluation():
    f = request.files['recording']
    print(f)
    threshold = get_environment_percentile(f)
    id = storage.add_threshold(threshold)
    return id

@app.route('/evaluation/<evaluationId>', methods=['GET'])
def get_evaluation(evaluationId):
    measurements = storage.get_attempts(evaluationId)
    return measurements

@app.route('/evaluation/<evaluationId>/attempt', methods=['POST'])
def process_attempt(evaluationId):
    f = request.files['recording']
    print(f)
    syllable_count = request.args.get('syllableCount')
    term = request.args.get('word')
    if syllable_count is None:
        return 'Must provide syllable count.'
    if term is None:
        return 'Must provide attempted word.'

    method = request.args.get('method')
    if method is None or method == '':
        method = 'average'
    wsd = calculator.calculate_wsd(f, syllable_count, evaluationId, method)
    storage.add_attempt(evaluationId, term, wsd)
    return str(wsd)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)