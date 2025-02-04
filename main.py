import easyocr
from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename

reader = easyocr.Reader(['en'])

app = Flask(__name__)

# Define the upload folder
UPLOAD_FOLDER = './uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
def getFile(request):
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Secure the filename and save the image
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    return file_path




# Route to upload image and return OCR result
@app.route('/api/upload', methods=['POST'])
def upload_file():
    file_path = getFile(request)

    try:
        # Perform OCR using EasyOCR
        text = reader.readtext(file_path)
        m = ""
        for (bbox, text, prob) in text:
            m = m+" "+text
        return jsonify({'ocr_result': str(m)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/api/sample', methods=['POST'])
def sample():
    # if request is not json return error
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400
    # read json data from request
    data = request.get_json()
    # send response
    return jsonify(data), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8081, debug=True)
