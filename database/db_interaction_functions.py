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

    # this function creates a database in a MySQL database
def create_database(connection, db_name):
        # this appends the database name to the CREATE DATABASE statement
    query = "CREATE DATABASE IF NOT EXISTS " + db_name
        # this executes the query
    return execute_query(connection, query, "Database creation")

    # this function drops a database in a MySQL database
def drop_database(connection, db_name):
        # this appends the database name to the DROP DATABASE
    query = "DROP DATABASE IF EXISTS " + db_name
        # this executes the query
    return execute_query(connection, query, "Database drop")


def create_table(connection, db_name, table_name, columns):
        # this appends the database name to the USE statement
    query = "USE " + db_name
        # this executes the query
    execute_query(connection, query, "Database selection")
        # this appends the table name and columns to the CREATE TABLE statement
    query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"
        # this executes the query
    return execute_query(connection, query, "Table creation")

def drop_table(connection, db_name, table_name):
        # this appends the database name to the USE statement
    query = "USE " + db_name
        # this executes the query
    execute_query(connection, query, "Database selection")
        # this appends the table name to the DROP TABLE statement
    query = f"DROP TABLE IF EXISTS {table_name}"
        # this executes the query
    return execute_query(connection, query, "Table drop")

    # this function executes a query in a MySQL database
def execute_query(connection, query, message = "Query"):
        # this creates a cursor object to execute the query
    cursor = connection.cursor()
        # this try-except block attempts to execute the query
    try:
        cursor.execute(query)
        connection.commit()
            # this print statement indicates a successful query execution
        print(f"{message} executed successfully")
        return True
    except Error as err:
            # this print statement indicates an error in query execution
        print(f"{message} error: '{err}'")
        return False