from database.db_interaction_functions import *
from database.roles import *

#def connect_to_db(db_name = "database", show_success = False):
    #return connect_to_db(db_name, show_success)

    # this creates an account in the user table
def create_account(connection, first_name, last_name, username, email, password, payment_info, role = "Unapproved_Employee"):
        # check if the user table exists
    if table_exists(connection, "user"):
            # formats the values to be inserted into the user table
        columns = "username, first_name, last_name, email, password, role, payment_info"
        values = f"'{username}', '{first_name}', '{last_name}', '{email}', '{password}', '{role}', '{payment_info}'"
            # inserts the values into the user table
        return insert_into_table(connection, "user", columns, values)
    print("Failed to create account: user table does not exist")
    return False

    # this logs into an account using the user's username and password
def login(connection, username, password):
        # check if the user table exists
    if table_exists(connection, "user"):
        db_password = select_value_from_table(connection, "user", "password", f"WHERE username = '{username}'", False, False, True)[0]
            # if the password is correct return True
        if db_password == password:
            print(f"Login successful: {username}")
            return True
        print(f"Failed to login: incorrect password")
        return False
    print("Failed to login: user table does not exist")
    return False

    # this accesses an accounts First Name, Last Name, Role, and Payment Info using the user's username and password
def access_account_information(connection, username, password):
        # check if the user table exists
    if table_exists(connection, "user"):
            # obtains the password from the user table
        db_password = select_value_from_table(connection, "user", "password", f"WHERE username = '{username}'", False, False, True)[0]
            # if the password is correct return the user's First Name, Last Name, Role, and Payment Info
        if db_password == password:
            desired_values = "first_name, last_name, email, role, payment_info"
            return select_value_from_table(connection, "user", desired_values, f"WHERE username = '{username}'", False, True, True)
        print(f"Failed to access account information: incorrect password")
        return False
    print("Failed to access account information: user table does not exist")
    return False

    # this obtains a user's role using their username and password
def get_user_role(connection, username, password):
        # check if the user table does not exist
    if not table_exists(connection, "user"):
        print("Failed to access account information: user table does not exist")
        return False

        # obtains the user's password from the user table
    db_password = select_value_from_table(connection, "user", "password", f"WHERE username = '{username}'", False, False, True)[0]
        # if the password given by the user is incorrect
    if db_password != password:
        print(f"Failed to access account information: incorrect password")
        return False

    # returns the role of the user
    return select_value_from_table(connection, "user", "role", f"WHERE username = '{username}'", False, True, True)[0]

    # this obtains the specific permission of a user
def get_user_permission(connection, username, password, permission):
    role = get_user_role(connection, username, password)
    return get_role_permission(connection, role, permission)

def get_user_count(connection):
    return select_value_from_table(connection, "user", "COUNT(*)", fetch_one = True)

    # this deletes an account in the user table
def delete_account(connection, username, password):
        # check if the user table exists
    if table_exists(connection, "user"):
        db_password = select_value_from_table(connection, "user", "password", f"WHERE username = '{username}'", False, False, True)[0]
            # if the password is correct delete the account
        if db_password == password:
            return delete_from_table(connection, "user", f"username = '{username}'")
        print(f"Failed to delete account: incorrect password")
        return False
    print("Failed to delete account: user table does not exist")
    return False

# main function
if __name__ == '__main__':
    connection = connect_to_db("database")
    table_name = "user"
    columns = ("username VARCHAR(255) NOT NULL, "
               "first_name VARCHAR(255) NOT NULL, "
               "last_name VARCHAR(255) NOT NULL, "
               "email VARCHAR(255) NOT NULL, "
               "password VARCHAR(255) NOT NULL, "
               "role VARCHAR(255) NOT NULL DEFAULT 'Unapproved_Employee', "
               "payment_info VARCHAR(255) NOT NULL, "
               "PRIMARY KEY (username, role)"
               "FOREIGN KEY (role) REFERENCES role(role_name)")

    delete_account(connection, "admin", "admin")
    drop_table(connection, table_name)

    create_table(connection, table_name, columns)
    create_account(connection, "admin", "admin", "admin", "admin", "admin", "admin", "Admin")
    create_account(connection, "manager", "manager", "manager", "manager", "manager", "manager", "Manager")
    create_account(connection, "employee", "employee", "employee", "employee", "employee", "employee", "Employee")
    create_account(connection, "unapproved_employee", "unapproved_employee", "unapproved_employee", "unapproved_employee", "unapproved_employee", "unapproved_employee")

    print(f"Account Information: {access_account_information(connection, "admin", "admin")}")
    print(f"User Role: {get_user_role(connection, 'admin', 'admin')}")
    print(f"User Permission: {get_user_permission(connection, 'manager', 'manager', 'payment_approve')}")