import db_interaction_functions as dbif

connection = dbif.create_server_connection("localhost", "root", "password1234")
db_name = "mydb"

dbif.drop_database(connection, db_name)
dbif.create_database(connection, db_name)

dbif.create_table(connection, db_name, "users", "id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), age INT")
