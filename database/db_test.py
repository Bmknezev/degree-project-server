import db_interaction_functions as dbif


connection = dbif.create_server_connection("test_db")
#db_name = "mydb"
table_name = "users"

dbif.delete_from_table(connection, table_name, "name = 'John Doe'")
dbif.delete_all_from_table(connection, table_name)
dbif.drop_table(connection, table_name,True)

dbif.create_table(connection, table_name, "id INTEGER PRIMARY KEY, name VARCHAR(255), age INT")
dbif.insert_into_table(connection, table_name, "name, age", "'John Doe', 25")
dbif.insert_into_table(connection, table_name, "name, age", "'Jane Doe', 22")
dbif.insert_into_table(connection, table_name, "name, age", "'John Smith', 32")
dbif.insert_into_table(connection, table_name, "name, age", "'Jane Smith', 29")

print(dbif.select_all_from_table(connection, table_name, show_results = False, show_execution_success = True))
dbif.select_from_table(connection, table_name, "WHERE name LIKE 'John Doe'")




#dbif.insert_into_table("real connection", table_name, "name, age", "'Real Person', -1")