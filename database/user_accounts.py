from database.db_interaction_functions import *
from database.roles import *

#def connect_to_db(db_name = "database", show_success = False):
    #return connect_to_db(db_name, show_success)

    # this creates an account in the user table
def create_account(connection, first_name, last_name, username, email, password, payment_info, role = None):
        # check if the user table exists
    if table_exists(connection, "user"):
            # formats the values to be inserted into the user table
        columns = "username, first_name, last_name, email, password, payment_info"
        values = f"'{username}', '{first_name}', '{last_name}', '{email}', '{password}', '{payment_info}'"
            # inserts the values into the user table
        user = insert_into_table(connection, "user", columns, values)
            # if the role is provided, add the role to the user
        if role:
            user_id = get_user_id(connection, username)
            add_role(connection, user_id, role)
        return user
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
            desired_values = "first_name, last_name, email, payment_info"
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

def get_user_count(connection):
    return select_value_from_table(connection, "user", "COUNT(*)", fetch_one = True)

def get_user_id(connection, username):
    return select_value_from_table(connection, "user", "user_id", f"WHERE username = '{username}'", fetch_one = True)[0]

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

    # this deletes an account in the user table from admin account
def admin_delete_account(connection, username):
        # check if the user table exists
    if table_exists(connection, "user"):
        return delete_from_table(connection, "user", f"username = '{username}'")
    print("Failed to delete account: user table does not exist")
    return False


def get_all_users(connection):
    if table_exists(connection, "user"):
        return select_value_from_table(connection, "user", f"first_name, last_name, username, email")


# main function
if __name__ == '__main__':
    connection = connect_to_db("database")
    table_name = "user"
    columns = ("user_id INTEGER PRIMARY KEY, "
               "username VARCHAR(255) NOT NULL, "
               "first_name VARCHAR(255) NOT NULL, "
               "last_name VARCHAR(255) NOT NULL, "
               "email VARCHAR(255) NOT NULL, "
               "password VARCHAR(255) NOT NULL, "
               "payment_info VARCHAR(255) NOT NULL")

    delete_account(connection, "admin", "admin")
    drop_table(connection, table_name)

    create_table(connection, table_name, columns)
    create_account(connection, "default", "account", "user", "defaultuser@email.com", "password", "credit card")
    create_account(connection, "admin", "admin", "admin", "admin@email.com", "admin", "credit card")
    create_account(connection, "John", "Smith", "johnsmith1973", "johnsmith1973@email.com", "password123", "credit card")
    create_account(connection, "Jane", "Doe", "janedoe1995", "janedoe1995@email.com", "password456", "paypal")

    print(f"Account Information: {access_account_information(connection, "admin", "admin")}")
