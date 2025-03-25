from database.db_interaction_functions import *
from database.user_accounts import *

def add_user_role(connection, user_id, role):
    if role != "approval_manager" and role != "financial_manager" and role != "system_admin":
        return False
    columns = "user_id, role"
    values = f"{user_id}, '{role}'"
    return insert_into_table(connection, "role", columns, values)

def remove_user_role(connection, user_id, role):
    if role != "approval_manager" and role != "financial_manager" and role != "system_admin":
        return False
    return delete_from_table(connection, "role", f"user_id = {user_id} AND role = '{role}'")

def get_all_roles(connection):
    return select_all_from_table(connection, "role")

def user_role_check(connection, user_id, role):
    if role != "approval_manager" and role != "financial_manager" and role != "system_admin":
        return "Not a valid role"
    return select_value_from_table(connection, "role", "COUNT(*)", f"WHERE user_id = {user_id} AND role = '{role}'", fetch_one = True, show_results = False)[0] > 0

def get_user_roles(connection, user_id):
    return select_tuple_from_table(connection, "role", f"WHERE user_id = {user_id}")

def get_role_count(connection):
    return select_value_from_table(connection, "role", "COUNT(*)", fetch_one = True)[0]

def create_role_table(connection):
    if table_exists(connection, "role"):
        return False
    columns = ("id INTEGER PRIMARY KEY, "
               "user_id INTEGER NOT NULL, "
               "role VARCHAR(255) NOT NULL CHECK (role IN ('approval_manager', 'financial_manager', 'system_admin')), "
               "FOREIGN KEY (user_id) REFERENCES user (id) ON DELETE CASCADE")
    return create_table(connection, "role", columns)

# main function
if __name__ == '__main__':
    connection = connect_to_db("database")
    table_name = 'role'
    columns = ("id INTEGER PRIMARY KEY, "
               "user_id INTEGER NOT NULL, "
               "role VARCHAR(255) NOT NULL CHECK (role IN ('approval_manager', 'financial_manager', 'system_admin')), "
               "FOREIGN KEY (user_id) REFERENCES user (id) ON DELETE CASCADE")

    drop_table(connection, table_name)

    create_table(connection, table_name, columns)
    admin_id = get_user_id(connection, "admin")
    user_id = get_user_id(connection, "user")
    add_user_role(connection, admin_id, "approval_manager")
    add_user_role(connection, admin_id, "financial_manager")
    add_user_role(connection, admin_id, "system_admin")

    print(user_role_check(connection, admin_id, "system_admin"))
    print(user_role_check(connection, user_id, "system_admin"))
    print(get_user_roles(connection, admin_id))
    print(get_user_roles(connection, user_id))
