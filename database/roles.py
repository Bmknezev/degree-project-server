from database.db_interaction_functions import *

def add_role(connection, role_name, invoice_read, invoice_upload, payment_approve, read_action_log, modify_roles, approve_new_users, delete_users):
    columns = "role_name, invoice_read, invoice_upload, payment_approve, read_action_log, modify_roles, approve_new_users, delete_users"
    values = f"'{role_name}', {invoice_read}, {invoice_upload}, {payment_approve}, {read_action_log}, {modify_roles}, {approve_new_users}, {delete_users}"
    return insert_into_table(connection, "role", columns, values)

def get_all_roles(connection):
    return select_all_from_table(connection, "role")

def get_role_permissions(connection, role_name):
    return select_tuple_from_table(connection, "role", f"WHERE role_name = '{role_name}'", show_results = False, fetch_one = True)[0]

def get_role_permission(connection, role_name, permission):
    return select_value_from_table(connection, "role", permission, f"WHERE role_name = '{role_name}'", fetch_one = True)[0]

def get_role_count(connection):
    return select_value_from_table(connection, "role", "COUNT(*)", fetch_one = True)[0]

def delete_role(connection, role_name):
    return delete_from_table(connection, "role", f"role_name = '{role_name}'")

# main function
if __name__ == '__main__':
    connection = connect_to_db("database")
    table_name = 'role'
    columns = ("role_name VARCHAR(255) PRIMARY KEY, "
               "invoice_read BOOLEAN NOT NULL DEFAULT 0, "
               "invoice_upload BOOLEAN NOT NULL DEFAULT 0, "
               "payment_approve INTEGER NOT NULL DEFAULT 0, "
               "read_action_log BOOLEAN NOT NULL DEFAULT 0, "
               "modify_roles BOOLEAN NOT NULL DEFAULT 0, "
               "approve_new_users BOOLEAN NOT NULL DEFAULT 0, "
               "delete_users BOOLEAN NOT NULL DEFAULT 0")

    delete_role(connection, "Admin")
    delete_role(connection, "Manager")
    delete_role(connection, "Employee")
    delete_role(connection, "Unapproved_Employee")
    drop_table(connection, table_name)

    create_table(connection, table_name, columns)
    add_role(connection, "Admin", 1, 1, 1000000, 1, 1, 1, 1)
    add_role(connection, "Manager", 1, 1, 50000, 1, 1, 1, 1)
    add_role(connection, "Employee", 1, 1, 0, 0, 0, 0, 0)
    add_role(connection, "Unapproved_Employee", 0, 0, 0, 0, 0, 0, 0)

    print(get_role_count(connection))
    print(get_all_roles(connection))
    print(get_role_permissions(connection, "Admin"))
    print(get_role_permission(connection, "Manager", "payment_approve"))