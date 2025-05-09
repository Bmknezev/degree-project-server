from database.db_interaction_functions import *
from database.roles import *
from database.approval_history import *
from database.vendors import *

def pay_invoice(connection, internal_id, paid_by, payment_method, payment_number, payment_date = None, payment_time = None, amount = None):
    internal_id = ''.join(filter(lambda x: x.isdigit(), str(internal_id)))
    paid_by = ''.join(filter(lambda x: x.isdigit(), str(paid_by)))
    if user_role_check(connection, paid_by, "financial_manager"):
        if check_for_payment(connection, internal_id):
            print("Failed to pay invoice: invoice already paid")
            return False
        if check_for_approval(connection, internal_id) == False:
            print("Failed to pay invoice: invoice not approved")
            return False
        if amount == None:
            amount = select_value_from_table(connection, "invoice", "total", f"WHERE internal_id = {internal_id}", fetch_one = True, show_results = False)[0]
        columns = "internal_id, paid_by, payment_method, amount, payment_number"
        values = f"{internal_id}, {paid_by}, '{payment_method}', {amount}, '{payment_number}'"
        if payment_date != None:
            columns += ", payment_date"
            values += f", '{payment_date}'"
        if payment_time != None:
            columns += ", payment_time"
            values += f", '{payment_time}'"
        return insert_into_table(connection, "payment_history", columns, values)
    else:
        print("Failed to pay invoice: user is not a financial manager")
        return False
    return False

def pay_invoices_by_vendor(connection, vendor_id, paid_by, payment_method, payment_number, payment_date = None, payment_time = None):
    if user_role_check(connection, paid_by, "financial_manager"):
        try:
            internal_ids = select_value_from_table(connection, "invoice", "internal_id", f"WHERE vendor = {vendor_id}", show_results = False)
            print(f"-Start of batch payment for vendor {vendor_id}")
            for internal_id in internal_ids:
                pay_invoice(connection, internal_id, paid_by, payment_method, payment_number, payment_date, payment_time)
            return True
        except:
            print("Failed to pay invoices: could not find invoices for vendor")
            return False
    else:
        print("Failed to pay invoices: user is not a financial manager")
        return False
    return False

def pay_multiple_invoices(connection, internal_ids, paid_by, payment_method, payment_number, payment_date = None, payment_time = None):
    if user_role_check(connection, paid_by, "financial_manager"):
        for internal_id in internal_ids:
            pay_invoice(connection, internal_id, paid_by, payment_method, payment_number, payment_date, payment_time)
        return True
    else:
        print("Failed to pay invoices: user is not a financial manager")
        return False
    return False

def check_for_payment(connection, internal_id):
    try:
        internal_id = ''.join(filter(lambda x: x.isdigit(), str(internal_id)))
        select_value_from_table(connection, "payment_history", "internal_id", f"WHERE internal_id = {internal_id}", fetch_one = True, show_results = False)[0]
        return True
    except:
        return False

def get_payment_date(connection, internal_id):
    try:
        return select_value_from_table(connection, "payment_history", "payment_date", f"WHERE internal_id = {internal_id}", fetch_one = True, show_results = False)[0]
    except:
        return False

def get_payment_time(connection, internal_id):
    try:
        return select_value_from_table(connection, "payment_history", "payment_time", f"WHERE internal_id = {internal_id}", fetch_one = True, show_results = False)[0]
    except:
        return False

def get_payer_id(connection, internal_id):
    return select_value_from_table(connection, "payment_history", "paid_by", f"WHERE internal_id = {internal_id}", fetch_one = True, show_results = False)[0]

def get_payer_first_name(connection, internal_id):
    return select_value_from_table(connection, "user", "first_name", f"WHERE user_id = {get_payer_id(connection, internal_id)}", fetch_one = True, show_results = False)[0]

def get_payer_last_name(connection, internal_id):
    return select_value_from_table(connection, "user", "last_name", f"WHERE user_id = {get_payer_id(connection, internal_id)}", fetch_one = True, show_results = False)[0]

def get_payer_username(connection, internal_id):
    return select_value_from_table(connection, "user", "username", f"WHERE user_id = {get_payer_id(connection, internal_id)}", fetch_one = True, show_results = False)[0]

def get_payments_by_user(connection, paid_by):
    return select_tuple_from_table(connection, "payment_history", f"WHERE paid_by = {paid_by}")

def get_payments_by_date(connection, payment_date):
    return select_tuple_from_table(connection, "payment_history", f"WHERE payment_date = {payment_date}")

def get_payment_amount(connection, internal_id):
    return select_value_from_table(connection, "payment_history", "amount", f"WHERE internal_id = {internal_id}", fetch_one = True, show_results = False)[0]

def get_payment_method(connection, internal_id):
    return select_value_from_table(connection, "payment_history", "payment_method", f"WHERE internal_id = {internal_id}", fetch_one = True, show_results = False)[0]

def get_payment_number(connection, internal_id):
    return select_value_from_table(connection, "payment_history", "payment_number", f"WHERE internal_id = {internal_id}", fetch_one = True, show_results = False)[0]

def create_payment_history_table(connection):
    if table_exists(connection, "payment_history"):
        return False
    columns = ("payment_id INTEGER PRIMARY KEY, "
               "internal_id INTEGER NOT NULL, "
               "payment_date DATE NOT NULL DEFAULT (date('now', 'localtime')), "
               "payment_time TIME NOT NULL DEFAULT (time('now', 'localtime')), "
               "paid_by INTEGER NOT NULL, "
               "payment_method VARCHAR(10) NOT NULL CHECK (payment_method IN ('cheque', 'paypal')), "
               "amount DECIMAL(10, 2) NOT NULL CHECK (amount >= 0), "
               "payment_number VARCHAR(255) NOT NULL, "
               "FOREIGN KEY (internal_id) REFERENCES invoice(internal_id), "
               "FOREIGN KEY (paid_by) REFERENCES user(user_id)")
    return create_table(connection, "payment_history", columns)


if __name__ == "__main__":
    connection = connect_to_db("database")

    drop_table(connection, "payment_history")
    create_payment_history_table(connection)

    #print(select_all_from_table(connection, table_name))
    user_id = get_user_id(connection, "user")
    admin_id = get_user_id(connection, "admin")
    print(pay_invoice(connection, 1, user_id, "cheque", 100))
    print(pay_invoice(connection, 1, admin_id, "cheque", 100))
    print(pay_invoice(connection, 2, admin_id, "cheque", 100))
    vendor1_id = get_vendor_id(connection, "internal1")
    print(pay_invoices_by_vendor(connection, vendor1_id, admin_id, "cheque", 100))

    print(f"Checking for payment: {check_for_payment(connection, 1)}")
    print(f"getting the payment date: {get_payment_date(connection, 1)}")
    print(f"getting the payment time: {get_payment_time(connection, 1)}")
    print(f"getting the payer's id: {get_payer_id(connection, 1)}")
    print(f"getting the payer's first name: {get_payer_first_name(connection, 1)}")
    print(f"getting the payer's last name: {get_payer_last_name(connection, 1)}")
    print(f"getting the payer's username: {get_payer_username(connection, 1)}")
    print(f"getting the payments by user: {get_payments_by_user(connection, user_id)}")
    print(f"getting the payments by date: {get_payments_by_date(connection, get_payment_date(connection, 1))}")
    print(f"getting the payment amount: {get_payment_amount(connection, 1)}")
    print(f"getting the payment method: {get_payment_method(connection, 1)}")
    print(f"getting the payment number: {get_payment_number(connection, 1)}")


