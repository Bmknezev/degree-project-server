import math
import os
import shutil
import easyocr
from flask import Flask, request
from werkzeug.utils import secure_filename
import test
from database.user_accounts import *
from database.invoices import *
from database.vendors import *

# Initialize the Flask app and EasyOCR reader
app = Flask(__name__)
reader = easyocr.Reader(['en'])

# Configure the upload folder and ensure it exists
UPLOAD_FOLDER = './uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# try to initialize ollama
try:
    print("Starting Ollama")
    os.popen(r"ollama.exe serve")
except:
    print("unable to start ollama")



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
    A simple echo handler (for testing).
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
    status_filter  = data.get('statusFilter', '')

    connection = connect_to_db("company_db")

    # Convert status filter into SQL restriction
    if status_filter == "Paid Invoices":
        restrictions = "status LIKE 'paid'"
    elif status_filter == "Waiting for Approval":
        restrictions = "status LIKE 'awaiting approval'"
    elif status_filter == "Waiting for Payment":
        restrictions = "status LIKE 'awaiting payment'"
    elif status_filter == "Unpaid Invoices":
        restrictions = "status IN ('awaiting approval', 'awaiting payment')"
    else:
        restrictions = "1"  # No filtering (default: show all invoices)

    total_invoices = get_invoice_count(connection)
    total_pages = math.ceil(total_invoices / page_size)  # Calculate total pages


    raw_invoices = get_invoices(connection, page_number, page_size, sort_by, sort_order, restrictions)
    connection.close()

    # Define column mappings
    column_names = [
        "internal_id", "invoice_number", "company", "subtotal", "tax", "total",
        "gl_account", "email", "issue_date", "due_date", "date_paid", "status", "description"
    ]

    # Convert raw database rows into JSON objects
    formatted_invoices = [dict(zip(column_names, row)) for row in raw_invoices]

    return {"invoices": formatted_invoices, "totalPages": total_pages}

def add_invoice_handler(data):
    connection = connect_to_db("company_db")
    vendor_id = get_vendor_id(connection, data['vendor'])
    add_invoice(
        connection=connection,
        invoice_number=data['invoiceNum'],
        vendor_id=vendor_id,
        total=data['total'],
        issue_date=data['issueDate'],
        due_date=data['due'],
        status="awaiting approval",
        subtotal=data.get('subTotal', "NULL"),
        tax=data.get('tax', "NULL"),
        gl_account=data['GL'],
        email=data['email'],
        date_paid="NULL",
        description="NULL"
    )

    # Get internal_id of last inserted row
    cursor = connection.cursor()
    cursor.execute("SELECT last_insert_rowid()")
    internal_id = cursor.fetchone()[0]

    connection.close()

    # Paths for files
    temp_filename = data.get('tempFilename')
    if temp_filename:
        old_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
        new_folder = os.path.join(app.config['UPLOAD_FOLDER'], "..", "stored_invoices")

        # Ensure destination folder exists
        os.makedirs(new_folder, exist_ok=True)

        new_filename = f"{internal_id}.png"
        new_path = os.path.join(new_folder, new_filename)

        if os.path.exists(old_path):
            shutil.move(old_path, new_path)
        else:
            return {"status": "failure", "message": f"File {temp_filename} not found in uploads folder."}

    return {"status": "success", "message": "Invoice added successfully."}

import base64
from flask import jsonify
import os

def get_invoice_image_handler(data):
    invoice_id = data.get('invoiceId', '')

    image_folder = "./stored_invoices"
    image_path = os.path.join(image_folder, f"{invoice_id}.png")

    if not os.path.exists(image_path):
        return {'status': 'failure', 'message': 'Invoice image not found'}

    try:
        with open(image_path, "rb") as img_file:
            encoded_image = base64.b64encode(img_file.read()).decode('utf-8')

        return {'status': 'success', 'imageData': encoded_image}

    except Exception as e:
        return {'status': 'failure', 'message': str(e)}


def get_invoice_by_ids_handler(data):
    """
    Get a list of specific invoices by internal_id list.
    """
    invoice_ids = data.get("invoiceIds", [])

    if not isinstance(invoice_ids, list) or not invoice_ids:
        return {
            "status": "error",
            "message": "Missing or invalid 'invoiceIds'. Expected a non-empty list."
        }

    connection = connect_to_db("company_db")

    try:
        raw_invoices = get_invoices_by_ids(connection, invoice_ids)

        # Define column mappings (must match your DB schema order)
        column_names = [
            "internal_id", "invoice_number", "company", "subtotal", "tax", "total",
            "gl_account", "email", "issue_date", "due_date", "date_paid", "status", "description"
        ]

        formatted_invoices = [dict(zip(column_names, row)) for row in raw_invoices]

        return {
            "status": "success",
            "invoices": formatted_invoices
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to fetch invoices: {str(e)}"
        }

    finally:
        connection.close()


def mark_invoices_paid_handler(data):
    invoice_ids = data.get("invoiceIds", [])
    connection = connect_to_db("company_db")
    cursor = connection.cursor()

    for invoice_id in invoice_ids:
        cursor.execute("UPDATE invoice SET status = 'paid', date_paid = CURRENT_DATE WHERE internal_id = ?",(invoice_id,))

    connection.commit()
    connection.close()
    return {"status": "success", "message": f"{len(invoice_ids)} invoice(s) marked as paid."}


def create_account_handler(data):
    connection = connect_to_db("company_db")
    status = create_account(
        connection = connection,
        first_name = data['first_name'],
        last_name = data['last_name'],
        email = data['email'],
        username = data['username'],
        password = data['password'],
        payment_info = "NULL"
    )
    connection.close()

    if status:
        return {"status": "success", "message": "User created successfully."}
    return {"status": "failure", "message": "Failed to create account."}


# Add handler mapping
MESSAGE_HANDLERS = {
    'LOGIN': login_handler,
    'SEND_INVOICE': invoice_handler,
    'CONFIRM_INVOICE': confirm_handler,
    'ECHO': echo_handler,
    'GET_INVOICES': get_invoices_handler,
    'ADD_INVOICE': add_invoice_handler,
    'GET_INVOICE_IMAGE': get_invoice_image_handler,
    'GET_INVOICES_BY_IDS': get_invoice_by_ids_handler,
    'MARK_INVOICES_PAID': mark_invoices_paid_handler,
    'CREATE_ACCOUNT': create_account_handler
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
        print(message_data)
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
    app.run(host="0.0.0.0", port=8081, debug=False)
