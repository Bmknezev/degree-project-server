import math
import os
import shutil
import uuid

import reportlab

#pip install reportlab

import easyocr
from flask import Flask, request
from werkzeug.utils import secure_filename
import test
from database.user_accounts import *
from database.invoices import *
from database.vendors import *
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
import os
import datetime


import requests

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


# Store tokens in-memory
active_sessions = {}  # token -> username

#paypal varaibles
PAYPAL_CLIENT_ID = "AX0u4jwN98Yd7HVVyHqzqVDtjWpJpNQN0fANuBWFT5pgjEYWFzFxw0JPTMyMk0pK4mu4Q-34om47kV1X"
PAYPAL_CLIENT_SECRET = "EMjNTD2FRS61NoXJBuFgAtTR3BMfvzNJBBudRPEemIxGTQ7M00bMr43fLSjC7dHAZOc9WP7in9h6oSKO"
PAYPAL_API_BASE = "https://api-m.sandbox.paypal.com"


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
        # Generate a session token (UUID)
        token = str(uuid.uuid4())
        active_sessions[token] = username  # store session
        connection.close()
        return {
            "status": "success",
            "message": "Login successful",
            "token": token
        }
    else:
        connection.close()
        return {
            "status": "failure",
            "message": "Invalid credentials"
        }

def logout_handler(data):
    token = data.get("token")
    if token and token in active_sessions:
        del active_sessions[token]
        return {"status": "success", "message": "Logged out"}
    return {"status": "failure", "message": "Invalid or missing token"}

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
    Get invoices from database, join with vendor info.
    """
    page_number = data.get('pageNumber', 1)
    page_size = data.get('pageSize', 10)
    sort_by = data.get('sortBy', 'invoice_number')
    sort_order = data.get('sortOrder', 'ASC')
    status_filter  = data.get('statusFilter', '')

    connection = connect_to_db("company_db")

    # Build restriction
    if status_filter == "Paid Invoices":
        restrictions = "i.status LIKE 'paid'"
    elif status_filter == "Waiting for Approval":
        restrictions = "i.status LIKE 'awaiting approval'"
    elif status_filter == "Waiting for Payment":
        restrictions = "i.status LIKE 'awaiting payment'"
    elif status_filter == "Unpaid Invoices":
        restrictions = "i.status IN ('awaiting approval', 'awaiting payment')"
    else:
        restrictions = "1"



    # Join invoice and vendor table
    query = f"""
        SELECT 
            i.internal_id, i.invoice_number, v.vendor_name, i.subtotal, i.tax, i.total,
            i.gl_account, v.email, i.issue_date, i.due_date, de.date_edited, s.status, i.description
        FROM invoice i
        JOIN vendor v ON i.vendor = v.vendor_id
        LEFT JOIN status s ON i.internal_id = s.internal_id
        LEFT JOIN date_edited de ON i.internal_id = de.internal_id
        WHERE {restrictions}
        ORDER BY {sort_by} {sort_order}
        LIMIT ? OFFSET ?
    """
    cursor = connection.cursor()
    cursor.execute(query, (page_size, page_size * (page_number - 1)))
    rows = cursor.fetchall()

    # Build JSON array manually
    invoices_json = []
    for row in rows:
        invoice = {
            "internal_id": row[0],
            "invoice_number": row[1],
            "company": row[2],               # vendor_name
            "subtotal": row[3],
            "tax": row[4],
            "total": row[5],
            "gl_account": row[6],
            "email": row[7],                 # vendor email
            "issue_date": row[8],
            "due_date": row[9],
            "date_paid": row[10],
            "status": row[11],
            "description": row[12],
        }
        invoices_json.append(invoice)

    # Calculate total *filtered* invoice count
    count_query = f"""
        SELECT COUNT(*)
        FROM invoice i
        JOIN vendor v ON i.vendor = v.vendor_id
        WHERE {restrictions}
    """
    cursor.execute(count_query)
    total_invoices = cursor.fetchone()[0]
    total_pages = math.ceil(total_invoices / page_size)
    connection.close()

    if invoices_json:
        print("First invoice:", invoices_json[0])
    else:
        print("No invoices found in result.")

    return {"invoices": invoices_json, "totalPages": total_pages}

def add_invoice_handler(data):
    connection = connect_to_db("company_db")
    vendor_id = data.get('vendor_id')
    if not vendor_id:
        return {"status": "fail", "message": "Missing vendor_id"}

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
        date_edited="NULL",
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

def add_vendor_handler(data):
    connection = connect_to_db("company_db")
    name = data.get("name")
    gl = data.get("gl")
    payment = data.get("payment")
    address = data.get("address")
    email = data.get("email")
    add_vendor(connection,name,name,gl,payment,address,email)
    vendor_id = get_vendor_id(connection, name)
    connection.close()

    return {"status": "ok", "vendor_id": vendor_id}

def mark_invoices_paid_handler(data):
    invoice_ids = data.get("invoiceIds", [])
    connection = connect_to_db("company_db")
    cursor = connection.cursor()

    for invoice_id in invoice_ids:
        cursor.execute("UPDATE invoice SET status = 'paid', date_edited = CURRENT_DATE WHERE internal_id = ?",(invoice_id,))

    connection.commit()
    connection.close()
    return {"status": "success", "message": f"{len(invoice_ids)} invoice(s) marked as paid."}

def pay_with_paypal_handler(data):
    invoice_ids = data.get("invoiceIds", [])

    if not invoice_ids:
        return {"status": "error", "message": "Missing invoiceIds or vendor name."}

    # Step 1: Validate session & get sender email
    token = request.get_json().get("token")
    sender_username = active_sessions.get(token)
    if not sender_username:
        return {"status": "error", "message": "Invalid session."}

    connection = connect_to_db("company_db")
    cursor = connection.cursor()

    try:
        # Step 1: Get vendor_id from the first invoice
        cursor.execute(
            "SELECT vendor FROM invoice WHERE internal_id = ?",
            (invoice_ids[0],)
        )
        result = cursor.fetchone()
        if not result:
            return {"status": "error", "message": "Invoice not found."}
        vendor_id = result[0]

        # Step 2: Get vendor email
        cursor.execute(
            "SELECT vendor_name, email FROM vendor WHERE vendor_id = ?",
            (vendor_id,)
        )
        vendor_result = cursor.fetchone()
        if not vendor_result:
            return {"status": "error", "message": "Vendor not found."}

        vendor_name, vendor_email = vendor_result

        # Step 3: Calculate total amount
        query = f"""
            SELECT SUM(total) FROM invoice
            WHERE internal_id IN ({','.join(['?'] * len(invoice_ids))})
        """
        cursor.execute(query, invoice_ids)
        total_amount = cursor.fetchone()[0] or 0

        # Step 4: Get sender's email
        cursor.execute("SELECT email FROM user WHERE username = ?", (sender_username,))
        sender_email = cursor.fetchone()[0]

        # Send PayPal payout
        payout_result = send_paypal_payout("sb-ob2s233980163_api1.business.example.com", "sb-uxk4033773358@business.example.com", total_amount)

        # log PayPal batch ID
        print("PayPal payout sent:", payout_result.get("batch_header", {}).get("payout_batch_id"))
        payout_id = payout_result["batch_header"]["payout_batch_id"]

        # Step 6: Mark invoices as paid
        cursor.executemany(
            "UPDATE invoice SET status = 'paid', date_edited = CURRENT_DATE WHERE internal_id = ?",
            [(iid,) for iid in invoice_ids]
        )
        connection.commit()

        # Path setup
        receipt_filename = f"receipt_{payout_id}.pdf"
        receipt_path = os.path.join("receipts", receipt_filename)  # Store in a subfolder, or temp dir

        os.makedirs("receipts", exist_ok=True)

        generate_receipt(
            save_path=receipt_path,
            paid_by=sender_username,
            vendor_name=vendor_name,
            amount=total_amount,  # You can calculate this via SQL or sum on frontend
            payment_number=payout_id,
            invoice_ids=invoice_ids
        )

        with open(receipt_path, "rb") as f:
            encoded_pdf = base64.b64encode(f.read()).decode("utf-8")

        return {
            "status": "success",
            "message": f"Paid ${total_amount:.2f} to {vendor_email} via PayPal.",
            "paypal_batch_id": payout_id,
            "receiptData": encoded_pdf,
            "receiptFilename": receipt_filename
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        connection.close()



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

def get_all_users_handler(data):
    connection = connect_to_db("company_db")
    result = get_all_users(connection)
    # Build JSON array manually
    users_json = []
    for row in result:
        users = {
            "first_name": row[0],
            "last_name": row[1],
            "username": row[2],  # vendor_name
            "email": row[3]
        }
        users_json.append(users)
    return {"users": users_json}

def admin_delete_account_handler(data):
    connection = connect_to_db("company_db")
    return admin_delete_account(connection, data.get("username"))


def update_vendor_handler(data):
    connection = connect_to_db("company_db")
    name = data.get("name")
    gl = data.get("gl")
    payment = data.get("payment")
    address = data.get("address")
    email = data.get("email")

    cursor = connection.cursor()
    cursor.execute("""
        UPDATE vendor
        SET default_gl_account = ?, payment_info = ?, address = ?, email = ?
        WHERE vendor_name = ?
    """, (gl, payment, address, email, name))

    vendor_id = get_vendor_id(connection, name)

    connection.commit()
    connection.close()

    return {"status": "ok", "vendor_id": vendor_id}

def get_all_vendors_handler(data):
    connection = connect_to_db("company_db")
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT vendor_id, vendor_name, email, address, default_gl_account FROM vendor")
        vendors = cursor.fetchall()

        vendor_list = []
        for vendor in vendors:
            vendor_list.append({
                "vendor_id": vendor[0],
                "name": vendor[1],
                "email": vendor[2],
                "address": vendor[3],
                "gl": vendor[4]
            })

        return {"status": "success", "vendors": vendor_list}

    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        connection.close()


def approve_invoices_handler(data):

    invoice_ids = data.get("invoiceIds", [])

    if not isinstance(invoice_ids, list) or not invoice_ids:
        return {
            "status": "error",
            "message": "Missing or invalid 'invoiceIds'. Expected a non-empty list."
        }

    connection = connect_to_db("company_db")
    cursor = connection.cursor()

    try:
        for invoice_id in invoice_ids:
            cursor.execute(
                "UPDATE invoice SET status = 'awaiting payment' WHERE internal_id = ?",
                (invoice_id,)
            )

        connection.commit()

        return {
            "status": "success",
            "message": f"{len(invoice_ids)} invoice(s) approved successfully."
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to approve invoices: {str(e)}"
        }

    finally:
        connection.close()

def get_vendor_by_id_handler(data):
    vendor_id = data.get("vendor_id")

    if not vendor_id:
        return {"status": "error", "message": "Missing vendor_id"}

    connection = connect_to_db("company_db")
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT vendor_id, vendor_name, email, address, default_gl_account
            FROM vendor
            WHERE vendor_id = ?
        """, (vendor_id,))
        row = cursor.fetchone()

        if not row:
            return {"status": "error", "message": "Vendor not found"}

        vendor_data = {
            "id": row[0],
            "name": row[1],
            "email": row[2],
            "address": row[3],
            "defaultGL": row[4]
        }

        return {"status": "success", "vendor": vendor_data}

    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        connection.close()



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
    'ADD_VENDOR': add_vendor_handler,
    'CREATE_ACCOUNT': create_account_handler,
    'UPDATE_VENDOR': update_vendor_handler,
    'GET_ALL_VENDORS': get_all_vendors_handler,
    'GET_ALL_USERS': get_all_users_handler,
    'ADMIN_DELETE_ACCOUNT': admin_delete_account_handler,
    'APPROVE_INVOICES' : approve_invoices_handler,
    'LOGOUT': logout_handler,
    'PAY_WITH_PAYPAL': pay_with_paypal_handler,
    'GET_VENDOR_BY_ID': get_vendor_by_id_handler,
}


# -----------------------------------------------------------------------------
# JSON Message Endpoint
# -----------------------------------------------------------------------------
@app.route('/api/message', methods=['POST'])
def api_message():
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400

    try:
        payload = request.get_json()
    except Exception as e:
        return jsonify({'error': f'Invalid JSON: {str(e)}'}), 400

    msg_type = payload.get('type', '').upper()
    message_data = payload.get('data', {})

    if msg_type != "LOGIN":
        token = payload.get('token')
        if token not in active_sessions:
            return jsonify({'error': 'Unauthorized'}), 401

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
# Paypal stuff
# -----------------------------------------------------------------------------
import requests

def get_paypal_access_token():
    response = requests.post(
        f"{PAYPAL_API_BASE}/v1/oauth2/token",
        headers={"Accept": "application/json"},
        data={"grant_type": "client_credentials"},
        auth=(PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET)
    )
    response.raise_for_status()
    return response.json()["access_token"]

def send_paypal_payout(sender_email, recipient_email, amount):
    access_token = get_paypal_access_token()

    payout_batch = {
        "sender_batch_header": {
            "sender_batch_id": str(uuid.uuid4()),
            "email_subject": "You have a payment from Invoice Manager",
        },
        "items": [
            {
                "recipient_type": "EMAIL",
                "amount": {
                    "value": f"{amount:.2f}",
                    "currency": "USD"
                },
                "receiver": recipient_email,
                "note": "Payment for approved invoices.",
                "sender_item_id": str(uuid.uuid4())
            }
        ]
    }

    response = requests.post(
        f"{PAYPAL_API_BASE}/v1/payments/payouts",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        },
        json=payout_batch
    )

    if response.status_code not in [200, 201]:
        raise Exception(f"PayPal payout failed: {response.text}")

    return response.json()

# -----------------------------------------------------------------------------
# Generates receipts
# -----------------------------------------------------------------------------

def generate_receipt(save_path, paid_by, vendor_name, amount, payment_number, invoice_ids):
    c = canvas.Canvas(save_path, pagesize=LETTER)
    width, height = LETTER

    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, height - 50, "Payment Receipt")

    # Details
    c.setFont("Helvetica", 12)
    y = height - 100
    c.drawString(50, y, f"Paid By (User ID): {paid_by}")
    y -= 20
    c.drawString(50, y, f"Vendor: {vendor_name}")
    y -= 20
    c.drawString(50, y, f"Payment Method: PayPal")
    y -= 20
    c.drawString(50, y, f"Transaction ID: {payment_number}")
    y -= 20
    c.drawString(50, y, f"Date: {datetime.date.today().isoformat()}")
    y -= 20
    c.drawString(50, y, f"Time: {datetime.datetime.now().strftime('%H:%M:%S')}")
    y -= 30
    c.drawString(50, y, f"Total Paid: ${amount:.2f}")
    y -= 30
    c.drawString(50, y, f"Invoices Paid:")

    for iid in invoice_ids:
        y -= 20
        c.drawString(70, y, f"- Invoice ID: {iid}")

    # Footer
    y -= 40
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(50, y, "Thank you for using our invoice system.")

    c.save()


# -----------------------------------------------------------------------------
# Run the Server
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    print("starting server...")
    app.run(host="0.0.0.0", port=8081, debug=False)
