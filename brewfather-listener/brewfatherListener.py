import json
import os

from flask import Flask, request
from flask_cors import CORS

from utilities.formatters import timestamp

BATCH_FOLDER = '/brewmoth/batches'
ALLOWED_EXTENSIONS = {'txt', 'json'}

app = Flask(__name__)
CORS(app)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/brewfather", methods=['GET', 'POST'])
def save_post():
    if request.method == 'POST':

        if request.is_json:
            received_json = request.get_json()
            time_stamp = timestamp() + ".batch"
            file = open(os.path.join(BATCH_FOLDER, time_stamp), "w")
            file.write(json.dumps(received_json))
            file.close()
        else:
            return "request was not a json"

        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    return "didn't get a post"


if __name__ == "__main__":
    app.run(host='0.0.0.0')
