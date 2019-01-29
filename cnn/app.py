from flask import Flask, request
from PIL import Image

import cnn, json
import numpy as np

class NumpyEncoder(json.JSONEncoder):
    '''
    Класс для перевода в json сложных объектов numpy.
    '''
    def default(self, obj):
        if isinstance(obj, (np.int_, np.intc, np.intp, np.int8,
            np.int16, np.int32, np.int64, np.uint8,
            np.uint16, np.uint32, np.uint64)):
            return int(obj)
        elif isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj,(np.ndarray,)):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


app = Flask(__name__)
global ml
global graph
ml, graph = cnn.init()

@app.route('/')
def index():
    return '''
    <form method="POST" action="/cnn" enctype="multipart/form-data">
    <input type="file" name="image"><br>
    <input type="submit" value="Classify File">
    </form>
    '''


@app.route('/cnn', methods=['POST'])
def run_cnn():
    result_error = {'status':'error'}
    attachment = request.files.get('image', None)
    if attachment:
        try:
            img = Image.open(attachment.stream)
            with graph.as_default():
                result = {
                        'status': 'OK',
                        'prediction': cnn.img_analyze(img, ml),
                        }
                result = json.dumps(result, cls=NumpyEncoder)
        except Exception as e:
            result_error['exeption'] = e
            result_error['reason'] = 'exception'
            result = json.dumps(result_error)
    else:
        result_error['reason'] = 'No file'
        result = json.dumps(result_error)

    return result

