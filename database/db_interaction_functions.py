#import mysql.connector
#from mysql.connector import Error
import sqlite3
from sqlite3 import Error
import pandas as pd

    # this function creates a connection to the MySQL database
def create_server_connection(host_name, user_name, user_password, db_name = "database"):
    connection = sqlite3.connect(db_name)
        # this try-except block attempts to connect to the database
    #try:
    #    connection = mysql.connector.connect(
    #        host = host_name,
    #        user = user_name,
    #        passwd = user_password
    #    )
            # this print statement indicates a successful connection
    #    print("MySQL Database connection successful")
    #except Error as err:
            # this print statement indicates an error in connection
    #    print(f"Error: '{err}'")

        # this returns the connection object
    return connection

# ---------------------- databases ----------------------
    # this function creates a database in a MySQL database
def create_database(connection, db_name, if_not_exists = True, show_success = True):
        # this appends the database name to the CREATE DATABASE statement
    query = f"CREATE DATABASE {'' if if_not_exists else 'IF NOT EXISTS'} {db_name}"
        # this executes the query
    return execute_query(connection, query, f"{db_name} database creation", show_success = show_success)


    # this function selects a database in a MySQL database
def select_database(connection, db_name, show_success = True, show_error = True):
        # this appends the database name to the USE statement
    query = "USE " + db_name
        # this executes the query
    return execute_query(connection, query, f"{db_name} database selection", show_success = show_success, show_error = show_error)


    # this function drops a database in a MySQL database
def drop_database(connection, db_name, if_exists = False, show_success = True):
        # this appends the database name to the DROP DATABASE
    query = f"DROP DATABASE {'' if if_exists else 'IF EXISTS'} {db_name}"
        # this executes the query
    return execute_query(connection, query, f"{db_name} database drop", show_success = show_success)


# ---------------------- tables ----------------------
    # this function creates a table in a MySQL database
def create_table(connection, table_name, columns, db_name = None, if_not_exists = False, show_selection_success = False, show_execution_success = True):
        # this checks if a database name is specified
    if db_name is not None:
            # this attempts to select the correct database
        if not select_database(connection, db_name, show_success = show_selection_success):
                # this returns False if the query fails
            return False

        # this appends the table name and columns to the CREATE TABLE statement
    query = f"CREATE TABLE {'' if if_not_exists else 'IF NOT EXISTS'} {table_name} ({columns})"
        # this executes the query
    return execute_query(connection, query, f"{table_name} table creation", show_success = show_execution_success)


    # this function inserts a tuple into a table from a MySQL database
def insert_into_table(connection, table_name, columns, values, db_name = None, show_selection_success = False, show_execution_success = True):
        # this checks if a database name is specified
    if db_name is not None:
            # this attempts to select the correct database
        if not select_database(connection, db_name, show_success = show_selection_success):
                # this returns False if the query fails
            return False

        # this appends the table name, columns, and values to the INSERT INTO statement
    query = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
        # this executes the query
    return execute_query(connection, query, f"{table_name} row insertion", show_success = show_execution_success)


    # this function selects all tuples fulfilling an argument from a table in a MySQL database
def select_from_table(connection, table_name, arguments, db_name = None, show_results = True, show_selection_success = False, show_execution_success = True):
        # this checks if a database name is specified
    if db_name is not None:
            # this attempts to select the correct database
        if not select_database(connection, db_name, show_success = show_selection_success):
                # this returns False if the query fails
            return False

        # this appends the table name and arguments to the SELECT statement
    query = f"SELECT * FROM {table_name} {arguments}"
        # this executes the query
    return execute_query(connection, query, f"{table_name} row selection", show_results = show_results, show_success = show_execution_success)


    # this function selects all tuples from a table in a MySQL database
def select_all_from_table(connection, table_name, db_name = None, show_results = True, show_selection_success = False, show_execution_success = True):
        # this checks if a database name is specified
    if db_name is not None:
            # this attempts to select the correct database
        if not select_database(connection, db_name, show_success = show_selection_success):
                # this returns False if the query fails
            return False

        # this appends the table name to the SELECT statement
    query = f"SELECT * FROM {table_name}"
        # this executes the query
    return execute_query(connection, query, f"{table_name} all rows selection", show_results = show_results, show_success = show_execution_success)


    # this function deletes a tuple from a table in a MySQL database
def delete_from_table(connection, table_name, condition, db_name = None, show_selection_success = False, show_execution_success = True):
        # this checks if a database name is specified
    if db_name is not None:
            # this attempts to select the correct database
        if not select_database(connection, db_name, show_success = show_selection_success):
                # this returns False if the query fails
            return False

        # this appends the table name and condition to the DELETE FROM statement
    query = f"DELETE FROM {table_name} WHERE {condition}"
        # this executes the query
    return execute_query(connection, query, f"{table_name} row deletion", show_success = show_execution_success)


    # this function drops a table in a MySQL database
def drop_table(connection, table_name, db_name = None, if_exists = False, show_selection_success = False, show_execution_success = True):
        # this checks if a database name is specified
    if db_name is not None:
            # this attempts to select the correct database
        if not select_database(connection, db_name, show_success = show_selection_success):
                # this returns False if the query fails
            return False

        # this appends the table name to the DROP TABLE statement
    query = f"DROP TABLE {'' if if_exists else 'IF EXISTS'} {table_name}"
        # this executes the query
    return execute_query(connection, query, f" {table_name} table drop", show_success = show_execution_success)


# ---------------------- queries ----------------------
    # this function executes a query in a MySQL database
def execute_query(connection, query, message = "Query", show_success = True, show_error = True, show_results = False):
        # this creates a cursor object to execute the query
    #cursor = connection.cursor(buffered = True)
    cursor = connection.cursor()
        # this try-except block attempts to execute the query
    try:
            # this executes the query
        cursor.execute(query)
        connection.commit()
            # this print statement indicates a successful query execution if show_success is True
        if show_success:
            print(f"{message} executed successfully")

        result = cursor.fetchall()
        if result:
            if show_results:
                print(pd.DataFrame(result))
            return result
        else:
            if show_results:
                print("No results")
        return True
    except Error as err:
            # this print statement indicates an error in query execution if show_error is True
        if show_error:
            print(f"{message} error: '{err}'")
        return False