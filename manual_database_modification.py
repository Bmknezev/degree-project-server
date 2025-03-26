from database.approval_history import *
from database.payment_history import *
from database.user_accounts import *
from database.vendors import *
from database.invoices import *
from database.views import *

# initialize the connection to the database
connection = connect_to_db("company_db")

    # create the user table
#drop_table(connection, "user")
#create_user_table(connection)

    # create the role table
#drop_table(connection, "role")
#create_role_table(connection)

    # create the invoice table
#drop_table(connection, "invoice")
#create_invoice_table(connection)

    # create the vendor table
#drop_table(connection, "vendor")
#create_vendor_table(connection)

    # create the upload history table
#drop_table(connection, "upload_history")
#create_upload_history_table(connection)

    # create the approval history table
#drop_table(connection, "approval_history")
#create_approval_history_table(connection)

    # create the payment history table
#drop_table(connection, "payment_history")
#create_payment_history_table(connection)

    # create the status view
#drop_status(connection)
#create_status(connection)

    # create the date edited view
#drop_date_edited(connection)
#create_date_edited(connection)



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
admin_id = get_user_id(connection, "admin")
totals = (100.00, 200.00, 300.00, 400.00, 500.00, 600.00, 700.00, 800.00, 900.00, 1000.00)
issue_dates = ("2021-01-01", "2021-02-01", "2021-03-01", "2021-04-01", "2021-05-01", "2021-06-01", "2021-07-01", "2021-08-01", "2021-09-01", "2021-10-01")
due_dates = ("2021-01-31", "2021-02-28", "2021-03-31", "2021-04-30", "2021-05-31", "2021-06-30", "2021-07-31", "2021-08-31", "2021-09-30", "2021-10-31")
#statuses = ("awaiting payment", "awaiting approval", "paid", "awaiting approval", "awaiting payment", "paid", "awaiting approval", "awaiting payment", "paid", "awaiting approval")
subtotals = (90.00, 180.00, 270.00, 360.00, 450.00, 540.00, 630.00, 720.00, 810.00, 900.00)
taxes = (10.00, 20.00, 30.00, 40.00, 50.00, 60.00, 70.00, 80.00, 90.00, 100.00)
emails = (None, None, "email@organization.ca", "email@corporation.org", "email.organization.ca", "email@enterprise.com", None, "email@megacorp.ca", "email@megacorp.ca", "email@establishment.net")

for i in range(0, 10):
    add_invoice(connection = connection,
                invoice_number = i + 1,
                vendor_id = vendor_ids[i],
                total = totals[i],
                issue_date = issue_dates[i],
                due_date = due_dates[i],
                #status = statuses[i],
                subtotal = subtotals[i],
                tax = taxes[i],
                email = emails[i],
                uploader_id = admin_id)
"""
    # approve and pay specific invoices
"""
admin_id = get_user_id(connection, "admin")
approve_invoice(connection, 1, admin_id)
approve_invoice(connection, 2, admin_id)
approve_invoice(connection, 4, admin_id)
approve_invoice(connection, 7, admin_id)
pay_invoice(connection, 1, admin_id, "paypal", "1234567890")
pay_invoice(connection, 2, admin_id, "cheque", "1234567890")

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

