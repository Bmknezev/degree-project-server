from database.db_interaction_functions import *

def new_upload_history(connection, internal_id, uploaded_by, uploader_role, upload_date = None, upload_time = None):
    columns = "internal_id, uploaded_by, uploader_role"
    values = f"{internal_id}, '{uploaded_by}', '{uploader_role}'"
    if upload_date != None:
        columns += ", upload_date"
        values += f", '{upload_date}'"
    if upload_time != None:
        columns += ", upload_time"
        values += f", '{upload_time}'"
    print(values)
    return insert_into_table(connection, "upload_history", columns, values)

if __name__ == "__main__":
    connection = connect_to_db("database")
    table_name = "upload_history"
    columns = ("upload_id INTEGER PRIMARY KEY, "
               "internal_id INTEGER NOT NULL, "
               "upload_date DATE NOT NULL DEFAULT CURRENT_DATE, "
               "upload_time TIME NOT NULL DEFAULT CURRENT_TIME, "
               "uploaded_by VARCHAR(255) NOT NULL, "
               "uploader_role VARCHAR(255) NOT NULL, "
               "FOREIGN KEY (internal_id) REFERENCES invoice(internal_id), "
               "FOREIGN KEY (uploaded_by) REFERENCES user(username), "
               "FOREIGN KEY (uploader_role) REFERENCES role(role_name)")

    drop_table(connection, table_name)
    create_table(connection, table_name, columns)

    new_upload_history(connection, 1, "admin", "Admin", upload_time = "12:00:00")
    new_upload_history(connection, 2, "admin", "Admin", "2021-01-01")
    new_upload_history(connection, 3, "admin", "Admin", "2021-01-01", "12:00:00")

    print(select_all_from_table(connection, table_name))