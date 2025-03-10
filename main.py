import os
import easyocr
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import re
import string
import cv2

import test
from database import invoices
from database.user_accounts import *
from database.invoices import *

# Initialize the Flask app and EasyOCR reader
app = Flask(__name__)
reader = easyocr.Reader(['en'])

# Configure the upload folder and ensure it exists
UPLOAD_FOLDER = './uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Initialize the connection to the database
#connection = connect_to_db("company_db")
#drop_table(connection, "user")
#if not table_exists(connection, "user"):
#create_table(connection, "user", "username VARCHAR(255) NOT NULL, first_name VARCHAR(255) NOT NULL, last_name VARCHAR(255) NOT NULL, email VARCHAR(255) NOT NULL, password VARCHAR(255) NOT NULL, role VARCHAR(255) NOT NULL, payment_info VARCHAR(255) NOT NULL, PRIMARY KEY (username, role)")
#columns = ("invoice_number VARCHAR(255) NOT NULL, company VARCHAR(25) NOT NULL, subtotal DECIMAL(10, 2) NOT NULL CHECK (subtotal >= 0), tax DECIMAL(10, 2) NOT NULL CHECK (tax >= 0), total DECIMAL(10, 2) NOT NULL CHECK (total >= 0 AND total >= subtotal), gl_account VARCHAR(255) NOT NULL, issue_date DATE NOT NULL, due_date DATE NOT NULL, date_paid DATE, status VARCHAR(17) NOT NULL CHECK (status IN ('awaiting approval', 'awaiting payment', 'paid')), description VARCHAR(255), PRIMARY KEY (invoice_number, company)")
#drop_table(connection, "invoice")
#create_table(connection, "invoice", columns)
#add_invoice(connection, "1", "company", 100.00, 10.00, 110.00, "gl_account", "2021-01-01", "2021-02-01", "2021-01-15", "awaiting payment", "description")
#add_invoice(connection, "2", "company", 200.00, 20.00, 220.00, "gl_account", "2021-02-01", "2021-03-01", "2021-02-15", "awaiting approval", "description")
#add_invoice(connection, "3", "organization", 349.56, 34.96, 384.52, "gl_account", "2021-03-01", "2021-04-01", "2021-03-15", "paid", "description")
#add_invoice(connection, "4", "corporation", 150.00, 15.00, 165.00, "gl_account", "2021-04-01", "2021-05-01", "2021-04-15", "awaiting approval", "description")
#add_invoice(connection, "5", "organization", 249.99, 24.99, 274.98, "gl_account", "2021-05-01", "2021-06-01", "2021-05-15", "awaiting payment", "description")
#add_invoice(connection, "6", "enterprise", 3000.00, 300.00, 3300.00, "gl_account", "2021-06-01", "2021-07-01", "2021-06-15", "paid", "description")
#add_invoice(connection, "7", "enterprise", 500.00, 50.00, 550.00, "gl_account", "2021-07-01", "2021-08-01", "2021-07-15", "awaiting approval", "description")
#add_invoice(connection, "8", "megacorp", 1000.00, 100.00, 1100.00, "gl_account", "2021-08-01", "2021-09-01", "2021-08-15", "awaiting payment", "description")
#add_invoice(connection, "9", "megacorp", 2000.00, 200.00, 2200.00, "gl_account", "2021-09-01", "2021-10-01", "2021-09-15", "paid", "description")
#add_invoice(connection, "10", "establishment", 3000.00, 300.00, 3300.00, "gl_account", "2021-10-01", "2021-11-01", "2021-10-15", "awaiting approval", "description")

#if select_tuple_from_table(connection, "user", "WHERE username = 'admin_user'", False, False) is None:
#create_account(connection, "Test", "Account", "user", "user@email.com", "password", "role", "payment_info")



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
    #if username == 'user' and password == 'pass':
    #    return {'status': 'success', 'message': 'Login successful'}
    #else:
    #    return {'status': 'failure', 'message': 'Invalid credentials'}
    connection = connect_to_db("company_db")
    if login(connection, username, password):
        connection.close()
        return {'status': 'success', 'message': 'Login successful'}
    else:
        connection.close()
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

def get_invoices_handler(data):
    """
    Get invoices from database
    """
    page_number = data.get('pageNumber', '')
    page_size = data.get('pageSize', '')
    sort_by = data.get('sortBy', '')
    sort_order = data.get('sortOrder', '')

    connection = connect_to_db("company_db")
    raw_invoices = get_invoices(connection, page_number, page_size, sort_by, sort_order)
    connection.close()

    # Define column mappings (Ensure these match the actual database columns)
    column_names = ["invoiceId", "sender", "subtotal", "tax", "totalAmount", "glAccount", "issueDate", "dueDate",
                    "paymentDate", "status", "description"]

    # Convert raw database rows into JSON objects
    formatted_invoices = [
        dict(zip(column_names, row)) for row in raw_invoices
    ]

    return {"invoices": formatted_invoices}  # Now returns proper JSON objects



# Map message types to their handlers.
# New message types can be added here.
MESSAGE_HANDLERS = {
    'LOGIN': login_handler,
    'SEND_INVOICE': invoice_handler,
    'CONFIRM_INVOICE': confirm_handler,
    'ECHO': echo_handler,  # For sample/test messages
    'GET_INVOICES': get_invoices_handler,
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
        data = test.OCR(file_path)

        return data, 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500





def draw_bounding_boxes(image_path, results):
        # Load the image using OpenCV
        image = cv2.imread(image_path)

        # Loop over each detected text result
        for result in results:
            bbox, text, _ = result  # Bounding box and text

            # Extract coordinates from the bounding box
            (tl_x, tl_y), (tr_x, tr_y), (br_x, br_y), (bl_x, bl_y) = bbox

            # Draw a rectangle around the detected text
            cv2.rectangle(image, (int(tl_x), int(tl_y)), (int(br_x), int(br_y)), (0, 255, 0), 2)

            # Optionally, put the detected text above the bounding box
            cv2.putText(image, text, (int(tl_x), int(tl_y) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        return image

def display_image(image):
        # Display the image in a window
        cv2.imshow('Invoice with Bounding Boxes', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()




def split_string_by_keywords(s, keywords):
    input_string = s.translate(str.maketrans('','',string.punctuation))
    # Create a regex pattern by joining keywords with | for OR condition
    pattern = r'\b(' + '|'.join(re.escape(keyword) for keyword in keywords) + r')\b'


    # Find the first occurrence of any keyword in the input string
    first_keyword_pos = min((input_string.find(keyword) for keyword in keywords if keyword in input_string),default=-1)

    if first_keyword_pos != -1:
        # Cut the string to start from the first occurrence of a keyword
        input_string = input_string[first_keyword_pos:]

    # Split the string based on the pattern and keep the delimiters (keywords)
    result = re.split(pattern, input_string)

    # Filter out empty strings if any exist
    result = [part for part in result if part]

    # Initialize an empty dictionary to store the keyword-text pairs
    result_dict = {}

    # Iterate through the result and extract the text after each keyword
    i = 0
    while i < len(result):
        keyword = result[i]
        if i + 1 < len(result):
            # The text after the keyword
            text = result[i + 1]
            # Add the keyword-text pair to the dictionary
            result_dict[keyword] = text
            i += 2  # Skip to the next keyword after the current text
        else:
            # If there's a keyword without any following text, just add it as key with empty string as value
            result_dict[keyword] = ''
            i += 1

    return result_dict


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
    print("starting server...")
    app.run(host="0.0.0.0", port=8081, debug=True)
