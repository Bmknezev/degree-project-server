from database.user_accounts import *
from database.vendors import *
from database.invoices import *

    # define table name
table_name = "invoice"
    # define invoice columns

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
"""
columns = ("vendor_id INTEGER PRIMARY KEY, "
            "vendor_name VARCHAR(255) NOT NULL, "
            "internal_name VARCHAR(255) NOT NULL, "
            "default_gl_account VARCHAR(255) NOT NULL, "
            "payment_info VARCHAR(255) NOT NULL, " 
            "address VARCHAR(255) NOT NULL, "
            "email VARCHAR(255) NOT NULL")
"""


    # initialize the connection to the database
connection = connect_to_db("company_db")

    # drop a table
#drop_table(connection, table_name)

    # create a table
#create_table(connection, table_name, columns)

    # add invoices
""
company_id = get_vendor_id(connection, "Company")
organization_id = get_vendor_id(connection, "Organization")
corporation_id = get_vendor_id(connection, "Corporation")
enterprise_id = get_vendor_id(connection, "Enterprise")
megacorp_id = get_vendor_id(connection, "Megacorp")
establishment_id = get_vendor_id(connection, "Establishment")

add_invoice(connection, "1", company_id, 100.00, "2021-01-01", "2021-02-01", 110.00, 10.00, "awaiting payment", "email@company.com")
add_invoice(connection, "2", company_id, 200.00, "gl_account", "email@company.com", "2021-02-01", "2021-03-01", "2021-02-15", "awaiting approval", 220.00, 20.00, "description")
add_invoice(connection, "3", organization_id, 349.56, "gl_account", "email@organization.ca", "2021-03-01", "2021-04-01", "2021-03-15", "paid", 384.52, 34.96, "description")
add_invoice(connection, "4", corporation_id, 150.00, "gl_account", "email@corporation.org", "2021-04-01", "2021-05-01", "2021-04-15", "awaiting approval", 165.00, 15.00, "description")
add_invoice(connection, "5", organization_id, 249.99, "gl_account", "email.organization.ca", "2021-05-01", "2021-06-01", "2021-05-15", "awaiting payment", 274.98, 24.99, "description")
add_invoice(connection, "6", enterprise_id, 3000.00, "gl_account", "email@enterprise.com", "2021-06-01", "2021-07-01", "2021-06-15", "paid", 3300.00, 300.00, "description")
add_invoice(connection, "7", enterprise_id, 500.00, "gl_account", "email@enterprise.com", "2021-07-01", "2021-08-01", "2021-07-15", "awaiting approval", 550.00, 50.00, "description")
add_invoice(connection, "8", megacorp_id, 1000.00, "gl_account", "email@megacorp.ca", "2021-08-01", "2021-09-01", "2021-08-15", "awaiting payment", 1100.00, 100.00, "description")
add_invoice(connection, "9", megacorp_id, 2000.00, "gl_account", "email@megacorp.ca", "2021-09-01", "2021-10-01", "2021-09-15", "paid", 2200.00, 200.00, "description")
add_invoice(connection, "10", establishment_id, 3000.00, "gl_account", "email@establishment.net", "2021-10-01", "2021-11-01", "2021-10-15", "awaiting approval", 3300.00, 300.00, "description")
""
    # add vendors
"""
add_vendor(connection, "Company", "Company", "gl_account1", "payment_info1", "address1", "email1")
add_vendor(connection, "Organization", "Organization", "gl_account1", "payment_info1", "address1", "email1")
add_vendor(connection, "Corporation", "Corporation", "gl_account1", "payment_info1", "address1", "email1")
add_vendor(connection, "Enterprise", "Enterprise", "gl_account1", "payment_info1", "address1", "email1")
add_vendor(connection, "Megacorp", "Megacorp", "gl_account1", "payment_info1", "address1", "email1")
add_vendor(connection, "Establishment", "Establishment", "gl_account1", "payment_info1", "address1", "email1")
"""

