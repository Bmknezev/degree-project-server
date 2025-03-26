from database.db_interaction_functions import *
from database.vendors import *
from database.upload_history import *
from database.user_accounts import *

def add_invoice(connection, invoice_number, vendor_id, total, issue_date, due_date, uploader_id, subtotal = None, tax = None, gl_account = None, email = None, description = None):
    columns = "invoice_number, vendor, total, gl_account, issue_date, due_date"
        # removes any character from the total value that is not a digit or a period
    total = ''.join(filter(lambda x: x.isdigit() or x == '.', str(total)))
        # removes any character from the vendor_id value that is not a digit
    vendor_id = ''.join(filter(lambda x: x.isdigit(), str(vendor_id)))
        # if the gl_account is not provided, set it to the default gl account for the vendor
    if gl_account == None:
        gl_account = get_gl_account_from_vendor(connection, vendor_id)
    values = f"'{invoice_number}', '{vendor_id}', {total}, '{gl_account}', '{issue_date}', '{due_date}'"
    if subtotal != None:
        columns += ", subtotal"
            # removes any character from the subtotal value that is not a digit or a period
        subtotal = ''.join(filter(lambda x: x.isdigit() or x == '.', str(subtotal)))
        values += f", {subtotal}"
    if tax != None:
        columns += ", tax"
            # removes any character from the tax value that is not a digit or a period
        tax = ''.join(filter(lambda x: x.isdigit() or x == '.', str(tax)))
        values += f", {tax}"
    if email != None:
        columns += ", email"
        values += f", '{email}'"
    if description != None:
        columns += ", description"
        values += f", '{description}'"
    print(f"New invoices inserted {columns} = {values}")
    invoice = insert_into_table(connection, "invoice", columns, values)
    invoice_id = get_invoice_id(connection, invoice_number, vendor_id)
    upload = new_upload(connection, invoice_id, uploader_id)
    return invoice

def get_invoices(connection, page_number, page_size, sort_by, sort_order, restrictions = "1"):
    invoices = select_tuple_from_table(connection, "invoice", f" WHERE {restrictions} ORDER BY {sort_by} {sort_order} LIMIT {page_size} OFFSET {page_size * (page_number - 1)}")
    print(f" - {invoices}")
    return invoices

def get_invoice_count(connection):
    return select_value_from_table(connection, "invoice", "COUNT(*)", fetch_one = True)[0]

def get_invoice_id(connection, invoice_number, vendor_id):
    vendor_id = ''.join(filter(lambda x: x.isdigit() or x == '.', str(vendor_id)))
    return select_value_from_table(connection, "invoice", "internal_id", f" WHERE invoice_number LIKE '{invoice_number}' AND vendor = {vendor_id}", fetch_one = True)[0]

def get_invoices_by_ids(connection, invoice_ids):
    if not invoice_ids:
        return []

    # Create a comma-separated string of IDs for the SQL IN clause
    id_list = ','.join(str(int(id)) for id in invoice_ids)  # ensure IDs are integers
    return select_tuple_from_table(connection, "invoice", f" WHERE internal_id IN ({id_list})")


def create_invoice_table(connection):
    if table_exists(connection, "invoice"):
        return False
    columns = ("internal_id INTEGER PRIMARY KEY, "
               "invoice_number VARCHAR(255) NOT NULL, "
               "vendor INTEGER NOT NULL, "
               "subtotal DECIMAL(10, 2) NOT NULL CHECK (subtotal >= 0), "
               "tax DECIMAL(10, 2) NOT NULL CHECK (tax >= 0), "
               "total DECIMAL(10, 2) NOT NULL CHECK (total >= 0), "
               "gl_account VARCHAR(255) NOT NULL, "
               "email VARCHAR(255), "
               "issue_date DATE NOT NULL, "
               "due_date DATE NOT NULL, "
               "description VARCHAR(255), "
               "FOREIGN KEY (vendor) REFERENCES vendor(vendor_id)")
    return create_table(connection, "invoice", columns)


if __name__ == '__main__':
    # Initialize the connection to the database
    connection = connect_to_db("database")
    #drop_table(connection, table_name)
    create_invoice_table(connection)
    #vendor1_id = get_vendor_id(connection, "internal1")
    #admin_id = get_user_id(connection, "admin")
    #print(get_invoices(connection, 1, 5, "invoice_number", "ASC"))
    #print(get_invoices(connection, 1, 5, "invoice_number", "DESC", "company LIKE 'company'"))

"""
    add_invoice(connection,
                invoice_number = "12345",
                vendor_id = vendor1_id,
                total = 100,
                issue_date = "2021-01-01",
                due_date = "2021-01-31",
                status = "awaiting approval",
                uploader_id = admin_id,
                subtotal = 90,
                tax = 10)
    add_invoice(connection,
                invoice_number = "67890",
                vendor_id = vendor1_id,
                total = 200,
                issue_date = "2021-02-01",
                due_date = "2021-02-28",
                status = "awaiting payment",
                uploader_id = admin_id,
                subtotal = 180,
                tax = 20)

    #print(get_invoices(connection, 1, 5, "invoice_number", "ASC"))
    #print(get_invoices(connection, 1, 5, "invoice_number", "DESC", "company LIKE 'company'"))
    """
