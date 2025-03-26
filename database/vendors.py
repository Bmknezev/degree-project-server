from database.db_interaction_functions import *

def add_vendor(connection, vendor_name, internal_name, default_gl_account, payment_info, address, email):
    columns = "vendor_name, internal_name, default_gl_account, payment_info, address, email"
    values = f"'{vendor_name}', '{internal_name}', '{default_gl_account}', '{payment_info}', '{address}', '{email}'"
    return insert_into_table(connection, "vendor", columns, values)

def get_vendors(connection):
    return select_all_from_table(connection, "vendor")

def get_vendor_id(connection, internal_name):
    try:
        s = select_value_from_table(connection, "vendor", "vendor_id", f"WHERE internal_name LIKE '{internal_name}'", fetch_one = True, show_results = False)[0]
        return s
    except:
        print("error")
        return False

def get_gl_account_from_vendor(connection, vendor_id):
    return select_value_from_table(connection, "vendor", "default_gl_account", f"WHERE vendor_id = {vendor_id}", fetch_one = True, show_results = False)[0]

def get_email_from_vendor(connection, vendor_id):
    return select_value_from_table(connection, "vendor", "email", f"WHERE vendor_id = {vendor_id}", fetch_one = True, show_results = False)[0]

def get_vendor_name(connection, vendor_id):
    return select_value_from_table(connection, "vendor", "vendor_name", f"WHERE vendor_id = {vendor_id}", fetch_one = True)[0]

def create_vendor_table(connection):
    if table_exists(connection, "vendor"):
        return False
    columns = ("vendor_id INTEGER PRIMARY KEY, "
               "vendor_name VARCHAR(255) NOT NULL, "
               "internal_name VARCHAR(255) NOT NULL, "
               "default_gl_account VARCHAR(255) NOT NULL, "
               "payment_info VARCHAR(255) NOT NULL, " 
               "address VARCHAR(255) NOT NULL, "
               "email VARCHAR(255) NOT NULL")
    return create_table(connection, "vendor", columns)

if __name__ == '__main__':
    connection = connect_to_db("database")

    drop_table(connection, "vendor")
    create_vendor_table(connection)

    add_vendor(connection, "vendor1", "internal1", "gl_account1", "payment_info1", "address1", "email1")

    print(select_all_from_table(connection, "vendor"))