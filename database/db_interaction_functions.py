import mysql.connector
from mysql.connector import Error
import pandas as pd

    # this function creates a connection to the MySQL database
def create_server_connection(host_name, user_name, user_password):
    connection = None
        # this try-except block attempts to connect to the database
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password
        )
            # this print statement indicates a successful connection
        print("MySQL Database connection successful")
    except Error as err:
            # this print statement indicates an error in connection
        print(f"Error: '{err}'")

    return connection

# ---------------------- databases ----------------------
    # this function creates a database in a MySQL database
def create_database(connection, db_name):
        # this appends the database name to the CREATE DATABASE statement
    query = "CREATE DATABASE IF NOT EXISTS " + db_name
        # this executes the query
    return execute_query(connection, query, f"{db_name} database creation")


    # this function drops a database in a MySQL database
def drop_database(connection, db_name):
        # this appends the database name to the DROP DATABASE
    query = "DROP DATABASE IF EXISTS " + db_name
        # this executes the query
    return execute_query(connection, query, f"{db_name} database drop")


# ---------------------- tables ----------------------
    # this function creates a table in a MySQL database
def create_table(connection, db_name, table_name, columns, show_selection_success = False, show_execution_success = True):
        # this appends the database name to the USE statement
    query = "USE " + db_name
        # this attempts to execute the query
    if not execute_query(connection, query, f"{db_name} database selection", show_success = show_selection_success):
            # this returns False if the query fails
        return False

        # this appends the table name and columns to the CREATE TABLE statement
    query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"
        # this executes the query
    return execute_query(connection, query, f"{table_name} table creation", show_success = show_execution_success)


    # this function inserts a tuple into a table from a MySQL database
def insert_into_table(connection, db_name, table_name, columns, values, show_selection_success = False, show_execution_success = True):
        # this appends the database name to the USE statement
    query = "USE " + db_name
        # this attempts to execute the query
    if not execute_query(connection, query, f"{db_name} database selection", show_success = show_selection_success):
            # this returns False if the query fails
        return False

        # this appends the table name, columns, and values to the INSERT INTO statement
    query = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
        # this executes the query
    return execute_query(connection, query, f"{table_name} row insertion", show_success = show_execution_success)


    # this function deletes a tuple from a table in a MySQL database
def delete_from_table(connection, db_name, table_name, condition, show_selection_success = False, show_execution_success = True):
        # this appends the database name to the USE statement
    query = "USE " + db_name
        # this attempts to execute the query
    if not execute_query(connection, query, f"{db_name} database selection", show_success = show_selection_success):
            # this returns False if the query fails
        return False

        # this appends the table name and condition to the DELETE FROM statement
    query = f"DELETE FROM {table_name} WHERE {condition}"
        # this executes the query
    return execute_query(connection, query, f"{table_name} row deletion", show_success = show_execution_success)


    # this function drops a table in a MySQL database
def drop_table(connection, db_name, table_name):
        # this appends the database name to the USE statement
    query = "USE " + db_name
        # this attempts to execute the query
    if not execute_query(connection, query, f"{db_name} database selection", show_success = False):
            # this returns False if the query fails
        return False

        # this appends the table name to the DROP TABLE statement
    query = f"DROP TABLE IF EXISTS {table_name}"
        # this executes the query
    return execute_query(connection, query, f" {table_name} table drop")


# ---------------------- queries ----------------------
    # this function executes a query in a MySQL database
def execute_query(connection, query, message = "Query", show_success = True, show_error = True):
        # this creates a cursor object to execute the query
    cursor = connection.cursor()
        # this try-except block attempts to execute the query
    try:
        cursor.execute(query)
        connection.commit()
            # this print statement indicates a successful query execution if show_success is True
        if show_success:
            print(f"{message} executed successfully")
        return True
    except Error as err:
            # this print statement indicates an error in query execution if show_error is True
        if show_error:
            print(f"{message} error: '{err}'")
        return False