from database.db_interaction_functions import *

columns = ("username VARCHAR(255) NOT NULL, "
           "first_name VARCHAR(255) NOT NULL, "
           "last_name VARCHAR(255) NOT NULL, "
           "email VARCHAR(255) NOT NULL, "
           "password VARCHAR(255) NOT NULL, "
           "role VARCHAR(255) NOT NULL, "
           "payment_info VARCHAR(255) NOT NULL, "
           "PRIMARY KEY (username, role)")

#def connect_to_db(db_name = "database", show_success = False):
    #return connect_to_db(db_name, show_success)

    # this creates an account in the user table
def create_account(connection, first_name, last_name, username, email, password, role, payment_info):
        # check if the user table exists
    if table_exists(connection, "user"):
            # formats the values to be inserted into the user table
        columns = "username, first_name, last_name, email, password, role, payment_info"
        values = f"'{username}', '{first_name}', '{last_name}', '{email}', '{password}', '{role}', '{payment_info}'"
            # inserts the values into the user table
        return insert_into_table(connection, "user", columns, values)
    print("Failed to create account: user table does not exist")
    return False

def login(connection, username, password):
        # check if the user table exists
    if table_exists(connection, "user"):
        db_password = select_value_from_table(connection, "user", "password", f"WHERE username = '{username}'", False, False, True)
            # if the password is correct return True
        if db_password[0] == password:
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
        db_password = select_value_from_table(connection, "user", "password", f"WHERE username = '{username}'", False, False, True)
            # if the password is correct return the user's First Name, Last Name, Role, and Payment Info
        if db_password[0] == password:
            desired_values = "first_name, last_name, email, role, payment_info"
            return select_value_from_table(connection, "user", desired_values, f"WHERE username = '{username}'", False, True, True)
        print(f"Failed to access account information: incorrect password")
        return False
    print("Failed to access account information: user table does not exist")
    return False


    # this deletes an account in the user table
def delete_account(connection, username, password):
        # check if the user table exists
    if table_exists(connection, "user"):
        db_password = select_value_from_table(connection, "user", "password", f"WHERE username = '{username}'", False, False, True)
            # if the password is correct delete the account
        if db_password[0] == password:
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
               "role VARCHAR(255) NOT NULL, "
               "payment_info VARCHAR(255) NOT NULL, "
               "PRIMARY KEY (username, role)")

    delete_account(connection, "admin", "admin")
    drop_table(connection, table_name)

    create_table(connection, table_name, columns)
    create_account(connection, "admin", "admin", "admin", "admin", "admin", "admin", "admin")
    print(f"Account Information: {access_account_information(connection, "admin", "admin")}")