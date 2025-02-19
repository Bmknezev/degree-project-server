import db_interaction_functions as dbif

connection = dbif.create_server_connection("localhost", "root", "password1234")
db_name = "mydb"
table_name = "users"

dbif.drop_database(connection, db_name)
dbif.create_database(connection, db_name)

dbif.create_table(connection, db_name, table_name, "id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), age INT")
dbif.insert_into_table(connection, db_name, table_name, "name, age", "'John Doe', 25")
dbif.insert_into_table(connection, db_name, table_name, "name, age", "'Jane Doe', 22")
dbif.insert_into_table(connection, db_name, table_name, "name, age", "'John Smith', 32")
dbif.insert_into_table(connection, db_name, table_name, "name, age", "'Jane Smith', 29")

dbif.select_all_from_table(connection, db_name, table_name)
dbif.select_from_table(connection, db_name, table_name, "WHERE name LIKE 'John Doe'")