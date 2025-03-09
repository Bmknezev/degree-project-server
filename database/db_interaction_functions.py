#import mysql.connector
#from mysql.connector import Error
import sqlite3
from sqlite3 import Error
import pandas as pd

    # this function creates a connection to the sqlite3 database
def connect_to_db(db_name = "database", show_success = True):
    connection = sqlite3.connect(db_name)
    if show_success:
        if connection:
            print(f"Connection to {db_name} database successful")
    return connection

# ---------------------- databases ----------------------
    # this function creates a database in a MySQL database
#def create_database(connection, db_name, if_not_exists = True, show_success = True):
        # this appends the database name to the CREATE DATABASE statement
    #query = f"CREATE DATABASE {'' if if_not_exists else 'IF NOT EXISTS'} {db_name}"
        # this executes the query
    #return execute_query(connection, query, f"{db_name} database creation", show_success = show_success)


    # this function selects a database in a MySQL database
#def select_database(connection, db_name, show_success = True, show_error = True):
        # this appends the database name to the USE statement
    #query = "USE " + db_name
        # this executes the query
    #return execute_query(connection, query, f"{db_name} database selection", show_success = show_success, show_error = show_error)


    # this function drops a database in a MySQL database
#def drop_database(connection, db_name, if_exists = False, show_success = True):
        # this appends the database name to the DROP DATABASE
    #query = f"DROP DATABASE {'' if if_exists else 'IF EXISTS'} {db_name}"
        # this executes the query
    #return execute_query(connection, query, f"{db_name} database drop", show_success = show_success)


# ---------------------- tables ----------------------
    # this function checks if a table exists in a sqlite3 database
def table_exists(connection, table_name):
        # this creates a cursor object to execute the query
    cursor = connection.cursor()
        # this executes the query checking for the table
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        # this returns True if the table exists, False otherwise
    return cursor.fetchone() is not None

    # this function creates a table in a sqlite3 database
def create_table(connection, table_name, columns, if_not_exists = False, show_execution_success = True):
        # this appends the table name and columns to the CREATE TABLE statement
    query = f"CREATE TABLE {'' if if_not_exists else 'IF NOT EXISTS'} {table_name} ({columns})"
        # this executes the query
    return execute_query(connection, query, f"{table_name} table creation", show_success = show_execution_success)


    # this function inserts a tuple into a table from a sqlite3 database
def insert_into_table(connection, table_name, columns, values, show_execution_success = True):
        # this appends the table name, columns, and values to the INSERT INTO statement
    query = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
        # this executes the query
    return execute_query(connection, query, f"{table_name} row insertion", show_success = show_execution_success)


    # this function selects all tuples fulfilling an argument from a table in a sqlite3 database
def select_tuple_from_table(connection, table_name, arguments, show_results = True, show_execution_success = True, fetch_one = False):
        # this appends the table name and arguments to the SELECT statement
    query = f"SELECT * FROM {table_name} {arguments}"
        # this executes the query
    return execute_query(connection, query, f"{table_name} row selection", show_results = show_results, show_success = show_execution_success)

   # this function selects a value from a tuple fulfilling an argument from a table in a sqlite3 database
def select_value_from_table(connection, table_name, value, arguments, show_results = True, show_execution_success = True, fetch_one = False):
        # this appends the table name and arguments to the SELECT statement
    query = f"SELECT {value} FROM {table_name} {arguments}"
        # this executes the query
    return execute_query(connection, query, f"{table_name} row selection", show_results = show_results, show_success = show_execution_success, fetch_one = fetch_one)

    # this function selects all tuples from a table in a sqlite3 database
def select_all_from_table(connection, table_name, show_results = True, show_execution_success = True, fetch_one = False):
        # this appends the table name to the SELECT statement
    query = f"SELECT * FROM {table_name}"
        # this executes the query
    return execute_query(connection, query, f"{table_name} all rows selection", show_results = show_results, show_success = show_execution_success, fetch_one = fetch_one)


    # this function deletes a tuple from a table in a sqlite3 database
def delete_from_table(connection, table_name, condition, show_execution_success = True):
        # this appends the table name and condition to the DELETE FROM statement
    query = f"DELETE FROM {table_name} WHERE {condition}"
        # this executes the query
    return execute_query(connection, query, f"{table_name} row deletion", show_success = show_execution_success)

    # this function deletes all tuples from a table in a sqlite3 database
def delete_all_from_table(connection, table_name, show_execution_success = True):
        # this appends the table name to the DELETE FROM statement
    query = f"DELETE FROM {table_name}"
        # this executes the query
    return execute_query(connection, query, f"{table_name} all rows deletion", show_success = show_execution_success)


    # this function drops a table in a sqlite3 database
def drop_table(connection, table_name, if_exists = False, show_execution_success = True):
        # this appends the table name to the DROP TABLE statement
    query = f"DROP TABLE {'' if if_exists else 'IF EXISTS'} {table_name}"
        # this executes the query
    return execute_query(connection, query, f"{table_name} table drop", show_success = show_execution_success)


# ---------------------- queries ----------------------
    # this function executes a query in a sqlite3 database
def execute_query(connection, query, message = "Query", show_success = True, show_error = True, show_results = False, fetch_one = False):
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
            # this fetches the first result of the query
        if fetch_one:
            result = cursor.fetchone()
            # this fetches all results of the query
        else:
            result = cursor.fetchall()
            # this checks if there are any results
        if result:
                # this prints the results if show_results is True
            if show_results:
                print(pd.DataFrame(result))
                # this returns the results
            return result
        else:
                # this print statement indicates no results if show_results is True
            if show_results:
                print("No results")

        return True
    except Error as err:
            # this print statement indicates an error in query execution if show_error is True
        if show_error:
            print(f"{message} error: '{err}'")
        return False