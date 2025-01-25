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


# Route to upload image and return OCR result
@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Secure the filename and save the image
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    try:
        # Perform OCR using EasyOCR
        text = reader.readtext(file_path)
        m = ""
        for (bbox, text, prob) in text:
            m = m+" "+text
        return jsonify({'ocr_result': str(m)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8081, debug=True)
