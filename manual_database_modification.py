from database.user_accounts import *
from database.vendors import *
from database.invoices import *

    # define table name
table_name = "invoice"

    # define user columns
"""
table_name = "user"
columns = ("user_id INTEGER PRIMARY KEY, "
               "username VARCHAR(255) NOT NULL UNIQUE, "
               "first_name VARCHAR(255) NOT NULL, "
               "last_name VARCHAR(255) NOT NULL, "
               "email VARCHAR(255) NOT NULL, "
               "password VARCHAR(255) NOT NULL, "
               "payment_info VARCHAR(255) NOT NULL")
"""

    # define role columns
"""
table_name = "role"
columns = ("id INTEGER PRIMARY KEY, "
           "user_id INTEGER NOT NULL, "
           "role VARCHAR(255) NOT NULL CHECK (role IN ('approval_manager', 'financial_manager', 'system_admin')), "
           "FOREIGN KEY (user_id) REFERENCES user (id) ON DELETE CASCADE")
"""

    # define invoice columns
"""
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
               "date_edited DATE, "
               "status VARCHAR(17) NOT NULL CHECK (status IN ('awaiting approval', 'awaiting payment', 'paid')), "
               "description VARCHAR(255), "
               "FOREIGN KEY (vendor) REFERENCES vendor(vendor_id)")
"""

    # define vendor columns
"""
table_name = "vendor"
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

    # add users
"""
create_account(connection = connection,
               first_name = "default",
               last_name = "account",
               username = "user",
               email = "defaultuser@email.com",
               password = "password",
               payment_info = "credit card")
create_account(connection = connection,
               first_name = "admin",
               last_name = "admin",
               username = "admin",
               email = "admin@email.com",
               password = "admin",
               payment_info = "credit card")
"""

    # add roles
"""
admin_id = get_user_id(connection, "admin")
add_user_role(connection = connection, user_id = admin_id, role = "approval_manager")
add_user_role(connection = connection, user_id = admin_id, role = "financial_manager")
add_user_role(connection = connection, user_id = admin_id, role = "system_admin")
"""

    # add invoices
"""
company_id = get_vendor_id(connection, "Company")
organization_id = get_vendor_id(connection, "Organization")
corporation_id = get_vendor_id(connection, "Corporation")
enterprise_id = get_vendor_id(connection, "Enterprise")
megacorp_id = get_vendor_id(connection, "Megacorp")
establishment_id = get_vendor_id(connection, "Establishment")

vendor_ids = (company_id, company_id, organization_id, corporation_id, organization_id, enterprise_id, enterprise_id, megacorp_id, megacorp_id, establishment_id)
totals = (100.00, 200.00, 349.56, 150.00, 249.99, 3000.00, 500.00, 1000.00, 2000.00, 3000.00)
issue_dates = ("2021-01-01", "2021-02-01", "2021-03-01", "2021-04-01", "2021-05-01", "2021-06-01", "2021-07-01", "2021-08-01", "2021-09-01", "2021-10-01")
due_dates = ("2021-01-31", "2021-02-28", "2021-03-31", "2021-04-30", "2021-05-31", "2021-06-30", "2021-07-31", "2021-08-31", "2021-09-30", "2021-10-31")
statuses = ("awaiting payment", "awaiting approval", "paid", "awaiting approval", "awaiting payment", "paid", "awaiting approval", "awaiting payment", "paid", "awaiting approval")
subtotals = (110.00, 220.00, None, 165.00, 274.98, 3300.00, None, 1100.00, 2200.00, 3300.00)
taxes = (10.00, None, 34.96, 15.00, 24.99, None, 50.00, 100.00, None, 300.00)
emails = (None, None, "email@organization.ca", "email@corporation.org", "email.organization.ca", "email@enterprise.com", None, "email@megacorp.ca", "email@megacorp.ca", "email@establishment.net")

for i in range(0, 10):
    add_invoice(connection = connection,
                invoice_number = i + 1,
                vendor_id = vendor_ids[i],
                total = totals[i],
                issue_date = issue_dates[i],
                due_date = due_dates[i],
                status = statuses[i],
                subtotal = subtotals[i],
                tax = taxes[i],
                email = emails[i])
"""

    # add vendors
"""
add_vendor(connection, "Company", "Company", "electrical", "payment_info1", "address1", "email1")
add_vendor(connection, "Organization", "Organization", "maintenance", "payment_info1", "address1", "email1")
add_vendor(connection, "Corporation", "Corporation", "general expenses", "payment_info1", "address1", "email1")
add_vendor(connection, "Enterprise", "Enterprise", "accounting", "payment_info1", "address1", "email1")
add_vendor(connection, "Megacorp", "Megacorp", "business", "payment_info1", "address1", "email1")
add_vendor(connection, "Establishment", "Establishment", "engineering", "payment_info1", "address1", "email1")
"""

