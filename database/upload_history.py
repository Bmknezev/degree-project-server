from database.db_interaction_functions import *

def new_upload(connection, internal_id, uploaded_by, upload_date = None, upload_time = None):
    internal_id = ''.join(filter(lambda x: x.isdigit(), str(internal_id)))
    uploaded_by = ''.join(filter(lambda x: x.isdigit(), str(uploaded_by)))
    if check_for_upload(connection, internal_id):
        print("Failed to upload invoice: invoice already uploaded")
        return False
    columns = "internal_id, uploaded_by"
    values = f"{internal_id}, '{uploaded_by}'"
    if upload_date != None:
        columns += ", upload_date"
        values += f", '{upload_date}'"
    if upload_time != None:
        columns += ", upload_time"
        values += f", '{upload_time}'"
    #print(values)
    return insert_into_table(connection, "upload_history", columns, values)

def check_for_upload(connection, internal_id):
    try:
        internal_id = ''.join(filter(lambda x: x.isdigit(), str(internal_id)))
        select_value_from_table(connection, "upload_history", "internal_id", f"WHERE internal_id = {internal_id}", fetch_one = True, show_results = False)[0]
        return True
    except:
        try:
            select_value_from_table(connection, "invoice", "internal_id", f"WHERE internal_id = {internal_id}", fetch_one = True, show_results = False)[0]
            print("Error, invoice exists in database but no record of upload")
            return False
        except:
            print("Error, invoice does not exist in database")
            return False

def get_upload_date(connection, internal_id):
    return select_value_from_table(connection, "upload_history", "upload_date", f"WHERE internal_id = {internal_id}", fetch_one = True, show_results = False)[0]

def get_upload_time(connection, internal_id):
    return select_value_from_table(connection, "upload_history", "upload_time", f"WHERE internal_id = {internal_id}", fetch_one = True, show_results = False)[0]

def get_uploader_id(connection, internal_id):
    return select_value_from_table(connection, "upload_history", "uploaded_by", f"WHERE internal_id = {internal_id}", fetch_one = True, show_results = False)[0]

def get_uploader_first_name(connection, internal_id):
    return select_value_from_table(connection, "user", "first_name", f"WHERE user_id = {get_uploader_id(connection, internal_id)}", fetch_one = True, show_results = False)[0]

def get_uploader_last_name(connection, internal_id):
    return select_value_from_table(connection, "user", "last_name", f"WHERE user_id = {get_uploader_id(connection, internal_id)}", fetch_one = True, show_results = False)[0]

def get_uploader_username(connection, internal_id):
    return select_value_from_table(connection, "user", "username", f"WHERE user_id = {get_uploader_id(connection, internal_id)}", fetch_one = True, show_results = False)[0]

def get_uploads_by_user(connection, uploaded_by):
    return select_tuple_from_table(connection, "upload_history", f"WHERE uploaded_by = {uploaded_by}")

def get_uploads_by_date(connection, upload_date):
    return select_tuple_from_table(connection, "upload_history", f"WHERE upload_date = {upload_date}")

def create_upload_history_table(connection):
    if table_exists(connection, "upload_history"):
        return False
    columns = ("upload_id INTEGER PRIMARY KEY, "
               "internal_id INTEGER NOT NULL, "
               "upload_date DATE NOT NULL DEFAULT CURRENT_DATE, "
               "upload_time TIME NOT NULL DEFAULT CURRENT_TIME, "
               "uploaded_by INTEGER NOT NULL, "
               "FOREIGN KEY (internal_id) REFERENCES invoice(internal_id), "
               "FOREIGN KEY (uploaded_by) REFERENCES user(user_id)")
    return create_table(connection, "upload_history", columns)

if __name__ == "__main__":
    connection = connect_to_db("database")
    table_name = "upload_history"
    columns = ("upload_id INTEGER PRIMARY KEY, "
               "internal_id INTEGER NOT NULL, "
               "upload_date DATE NOT NULL DEFAULT CURRENT_DATE, "
               "upload_time TIME NOT NULL DEFAULT CURRENT_TIME, "
               "uploaded_by INTEGER NOT NULL, "
               "FOREIGN KEY (internal_id) REFERENCES invoice(internal_id), "
               "FOREIGN KEY (uploaded_by) REFERENCES user(user_id)")

    #drop_table(connection, table_name)
    #create_table(connection, table_name, columns)

    #print(select_all_from_table(connection, table_name))
    print(f"Checking for upload: {check_for_upload(connection, 1)}")
    print(f"getting the upload date: {get_upload_date(connection, 1)}")
    print(f"getting the upload time: {get_upload_time(connection, 1)}")
    print(f"getting the uploader id: {get_uploader_id(connection, 1)}")
    print(f"getting the uploader first name: {get_uploader_first_name(connection, 1)}")
    print(f"getting the uploader last name: {get_uploader_last_name(connection, 1)}")
    print(f"getting the uploader username: {get_uploader_username(connection, 1)}")
    print(f"getting uploads by user: {get_uploads_by_user(connection, 1)}")
    print(f"getting uploads by date: {get_uploads_by_date(connection, '2021-04-01')}")
