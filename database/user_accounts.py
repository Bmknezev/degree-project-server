from db_interaction_functions import *

columns = ("user_id INTEGER PRIMARY KEY, "
           "first_name VARCHAR(255), "
           "last_name VARCHAR(255), "
           "username VARCHAR(255), "
           "email VARCHAR(255), "
           "password VARCHAR(255), "
           "role VARCHAR(255), "
           "payment_info VARCHAR(255)")

    # this creates an account in the user table
def create_account(connection, first_name, last_name, username, email, password, role, payment_info):
        # check if the user table exists
    if table_exists(connection, "user"):
            # formats the values to be inserted into the user table
        columns = "first_name, last_name, username, email, password, role, payment_info"
        values = f"'{first_name}', '{last_name}', '{username}', '{email}', '{password}', '{role}', '{payment_info}'"
            # inserts the values into the user table
        return insert_into_table(connection, "user", columns, values)
    print("Failed to create account: user table does not exist")
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

    delete_account(connection, "admin", "admin")
    drop_table(connection, table_name)

    create_table(connection, table_name, columns)
    create_account(connection, "admin", "admin", "admin", "admin", "admin", "admin", "admin")
    print(f"Account Information: {access_account_information(connection, "admin", "admin")}")