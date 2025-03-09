from database.db_interaction_functions import *

def create_invoice(connection, invoice_number, company, subtotal, tax, total, gl_account, issue_date, due_date, date_paid, status, description):
    columns = "invoice_number, company, subtotal, tax, total, gl_account, issue_date, due_date, date_paid, status, description"
    values = f"'{invoice_number}', '{company}', {subtotal}, {tax}, {total}, '{gl_account}', '{issue_date}', '{due_date}', '{date_paid}', '{status}', '{description}'"
    return insert_into_table(connection, "invoice", columns, values)





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
               "status VARCHAR(17) NOT NULL CHECK (status IN ('awaiting approval', 'awaiting payment', 'payed')), "
               "description VARCHAR(255), "
               "PRIMARY KEY (invoice_number, company)")


    drop_table(connection, table_name)

    create_table(connection, table_name, columns)
    create_invoice(connection, "1", "company", 100.00, 10.00, 110.00, "gl_account", "2021-01-01", "2021-02-01", "2021-01-15", "awaiting payment", "description")
    create_invoice(connection, "2", "company", 200.00, 20.00, 220.00, "gl_account", "2021-02-01", "2021-03-01", "2021-02-15", "awaiting approval", "description")
