import os
import easyocr
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename



# Initialize the Flask app and EasyOCR reader
app = Flask(__name__)
reader = easyocr.Reader(['en'])

# Configure the upload folder and ensure it exists
UPLOAD_FOLDER = './uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# -----------------------------------------------------------------------------
# Message Handlers
# -----------------------------------------------------------------------------
def login_handler(data):
    """
    Handler for login messages.
    Expected data: { "username": "...", "password": "..." }
    """
    username = data.get('username', '')
    password = data.get('password', '')
    # Dummy validation logic – replace with real authentication
    if username == 'user' and password == 'pass':
        return {'status': 'success', 'message': 'Login successful'}
    else:
        return {'status': 'failure', 'message': 'Invalid credentials'}


def invoice_handler(data):
    """
    Handler for processing invoices.
    Expected data: { "invoiceId": "...", ... }
    """
    invoice_id = data.get('invoiceId', '')
    # Insert your invoice processing logic here
    return {'status': 'success', 'message': f'Invoice {invoice_id} processed.'}


def confirm_handler(data):
    """
    Handler for confirming invoice data.
    Expected data: { "invoiceId": "...", "confirmed": true/false }
    """
    invoice_id = data.get('invoiceId', '')
    confirmed = data.get('confirmed', False)
    action = 'confirmed' if confirmed else 'rejected'
    return {'status': 'success', 'message': f'Invoice {invoice_id} {action}.'}


def echo_handler(data):
    """
    A simple echo handler (useful for testing).
    """
    return data


# Map message types to their handlers.
# New message types can be added here.
MESSAGE_HANDLERS = {
    'LOGIN': login_handler,
    'SEND_INVOICE': invoice_handler,
    'CONFIRM_INVOICE': confirm_handler,
    'ECHO': echo_handler,  # For sample/test messages
}


# -----------------------------------------------------------------------------
# JSON Message Endpoint
# -----------------------------------------------------------------------------
@app.route('/api/message', methods=['POST'])
def api_message():
    """
    Endpoint that accepts a JSON payload with a 'type' field and optional 'data'.
    Dispatches the message to the appropriate handler.

    Expected JSON format:
      {
        "type": "LOGIN",         // or SEND_INVOICE, CONFIRM_INVOICE, etc.
        "data": { ... }          // data specific to the message type
      }
    """
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400

    try:
        payload = request.get_json()
    except Exception as e:
        return jsonify({'error': f'Invalid JSON: {str(e)}'}), 400

    msg_type = payload.get('type', '').upper()
    message_data = payload.get('data', {})

    if not msg_type:
        return jsonify({'error': 'Message type not specified'}), 400

    handler = MESSAGE_HANDLERS.get(msg_type)
    if handler is None:
        return jsonify({'error': f'Unsupported message type: {msg_type}'}), 400

    try:
        response = handler(message_data)
        return jsonify(response), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# -----------------------------------------------------------------------------
# File Upload Endpoint for OCR
# -----------------------------------------------------------------------------
def save_uploaded_file(req):
    """
    Helper function to retrieve and save an uploaded file.
    """
    if 'file' not in req.files:
        return None, jsonify({'error': 'No file part in the request'}), 400

    file = req.files['file']
    if file.filename == '':
        return None, jsonify({'error': 'No selected file'}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    return file_path, None, None


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """
    Endpoint to handle file uploads (for OCR).
    The uploaded file is saved, processed with EasyOCR, and the extracted text is returned.
    """
    file_path, error_resp, error_code = save_uploaded_file(request)
    if error_resp:
        return error_resp, error_code

    try:
        # Perform OCR on the saved file
        ocr_results = reader.readtext(file_path)
        # Concatenate the detected text segments into one string
        extracted_text = " ".join([text for (_, text, _) in ocr_results])
        return jsonify({'ocr_result': extracted_text}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# -----------------------------------------------------------------------------
# Optional: Sample Endpoint (Echoes back the JSON received)
# -----------------------------------------------------------------------------
@app.route('/api/sample', methods=['POST'])
def sample():
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400
    try:
        data = request.get_json()
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    return jsonify(data), 200


# -----------------------------------------------------------------------------
# Run the Server
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8081, debug=True)
