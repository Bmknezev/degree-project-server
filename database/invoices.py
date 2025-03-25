from database.db_interaction_functions import *
from database.vendors import *

def add_invoice(connection, invoice_number, vendor_id, total, issue_date, due_date, status, subtotal = None, tax = None, gl_account = None, email = None, date_paid = None, description = None):
    columns = "invoice_number, vendor, total, gl_account, issue_date, due_date, status"
        # removes any character from the total value that is not a digit or a period
    total = ''.join(filter(lambda x: x.isdigit() or x == '.', str(total)))
        # removes any character from the vendor_id value that is not a digit
    vendor_id = ''.join(filter(lambda x: x.isdigit(), str(vendor_id)))
        # if the gl_account is not provided, set it to the default gl account for the vendor
    if gl_account == None:
        gl_account = get_gl_account_from_vendor(connection, vendor_id)
    values = f"'{invoice_number}', '{vendor_id}', {total}, '{gl_account}', '{issue_date}', '{due_date}', '{status}'"
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
    if date_paid != None:
        columns += ", date_paid"
        values += f", '{date_paid}'"
    if description != None:
        columns += ", description"
        values += f", '{description}'"
    print(f"New invoices inserted {columns} = {values}")
    return insert_into_table(connection, "invoice", columns, values)

def get_invoices(connection, page_number, page_size, sort_by, sort_order, restrictions = "1"):
    return select_tuple_from_table(connection, "invoice", f" WHERE {restrictions} ORDER BY {sort_by} {sort_order} LIMIT {page_size} OFFSET {page_size * (page_number - 1)}")

def get_invoice_count(connection):
    return select_value_from_table(connection, "invoice", "COUNT(*)", fetch_one = True)[0]

def get_invoices_by_ids(connection, invoice_ids):
    if not invoice_ids:
        return []

    # Create a comma-separated string of IDs for the SQL IN clause
    id_list = ','.join(str(int(id)) for id in invoice_ids)  # ensure IDs are integers

    query = f"SELECT * FROM invoice WHERE internal_id IN ({id_list})"
    return select_tuple_from_table(connection, "invoice", f" WHERE internal_id IN ({id_list})")


if __name__ == '__main__':
    # Initialize the connection to the database
    connection = connect_to_db("database")
    table_name = "invoice"
    columns = ("internal_id INTEGER PRIMARY KEY, "
               "invoice_number VARCHAR(255) NOT NULL, "
               "vendor INTEGER NOT NULL, "
               "subtotal DECIMAL(10, 2) CHECK (subtotal >= 0), "
               "tax DECIMAL(10, 2) CHECK (tax >= 0), "
               "total DECIMAL(10, 2) NOT NULL CHECK (total >= 0), "
               "gl_account VARCHAR(255) NOT NULL, "
               "email VARCHAR(255), "
               "issue_date DATE NOT NULL, "
               "due_date DATE NOT NULL, "
               "date_paid DATE, "
               "status VARCHAR(17) NOT NULL CHECK (status IN ('awaiting approval', 'awaiting payment', 'paid')), "
               "description VARCHAR(255), "
               "FOREIGN KEY (vendor) REFERENCES vendor(vendor_id)")


    drop_table(connection, table_name)

    create_table(connection, table_name, columns)
    add_invoice(connection, "1", "company", 100.00, "gl_account", "example@company.com", "2021-01-01", "2021-02-01", "2021-01-15", "awaiting payment", 110.00, description = "description")
    add_invoice(connection, "2", "company", 200.00, "gl_account", "example@company.com", "2021-02-01", "2021-03-01", "2021-02-15", "awaiting approval", 220.00, 20.00, "description")

    print(get_invoices(connection, 1, 5, "invoice_number", "ASC"))
    print(get_invoices(connection, 1, 5, "invoice_number", "DESC", "company LIKE 'company'"))
