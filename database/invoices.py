from database.db_interaction_functions import *

def add_invoice(connection, invoice_number, company, subtotal, tax, total, gl_account, issue_date, due_date, date_paid, status, description):
    columns = "invoice_number, company, subtotal, tax, total, gl_account, issue_date, due_date, date_paid, status, description"
    values = f"'{invoice_number}', '{company}', {subtotal}, {tax}, {total}, '{gl_account}', '{issue_date}', '{due_date}', '{date_paid}', '{status}', '{description}'"
    return insert_into_table(connection, "invoice", columns, values)

def get_invoices(connection, page_number, page_size, sort_by, sort_order, restrictions = "1"):
    return select_tuple_from_table(connection, "invoice", f" WHERE {restrictions} ORDER BY {sort_by} {sort_order} LIMIT {page_size} OFFSET {page_size * (page_number - 1)}")

def get_total_invoices(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM invoice")
    total = cursor.fetchone()[0]
    return total



if __name__ == '__main__':
    # Initialize the connection to the database
    connection = connect_to_db("database")
    table_name = "invoice"
    columns = ("invoice_number VARCHAR(255) NOT NULL, "
               "company VARCHAR(25) NOT NULL, "
               "subtotal DECIMAL(10, 2) NOT NULL CHECK (subtotal >= 0), "
               "tax DECIMAL(10, 2) NOT NULL CHECK (tax >= 0), "
               "total DECIMAL(10, 2) NOT NULL CHECK (total >= 0 AND total >= subtotal), "
               "gl_account VARCHAR(255) NOT NULL, "
               "issue_date DATE NOT NULL, "
               "due_date DATE NOT NULL, "
               "date_paid DATE, "
               "status VARCHAR(17) NOT NULL CHECK (status IN ('awaiting approval', 'awaiting payment', 'paid')), "
               "description VARCHAR(255), "
               "PRIMARY KEY (invoice_number, company)")


    drop_table(connection, table_name)

    create_table(connection, table_name, columns)
    add_invoice(connection, "1", "company", 100.00, 10.00, 110.00, "gl_account", "2021-01-01", "2021-02-01", "2021-01-15", "awaiting payment", "description")
    add_invoice(connection, "2", "company", 200.00, 20.00, 220.00, "gl_account", "2021-02-01", "2021-03-01", "2021-02-15", "awaiting approval", "description")

    print(get_invoices(connection, 1, 5, "invoice_number", "ASC"))
