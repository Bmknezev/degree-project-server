from db_interaction_functions import *


connection = connect_to_db("test_db")
#db_name = "mydb"
table_name = "users"

delete_from_table(connection, table_name, "name = 'John Doe'")
delete_all_from_table(connection, table_name)
drop_table(connection, table_name,True)

create_table(connection, table_name, "id INTEGER PRIMARY KEY, name VARCHAR(255), age INT")
columns = "name, age"
john_doe = "'John Doe', 25"
insert_into_table(connection, table_name, columns, john_doe)
insert_into_table(connection, table_name, "name, age", "'Jane Doe', 22")
insert_into_table(connection, table_name, "name, age", "'John Smith', 32")
insert_into_table(connection, table_name, "name, age", "'Jane Smith', 29")

print(select_all_from_table(connection, table_name, show_results = False, show_execution_success = True))
select_tuple_from_table(connection, table_name, "WHERE name LIKE 'John Doe'")




#insert_into_table("real connection", table_name, "name, age", "'Real Person', -1")