from database.db_interaction_functions import *
from database.roles import *
from database.upload_history import *

def approve_invoice(connection, internal_id, approved_by, approval_date = None, approval_time = None):
    if user_role_check(connection, approved_by, "approval_manager"):
        if check_for_approval(connection, internal_id):
            print("Failed to approve invoice: invoice already approved")
            return False
        if check_for_upload(connection, internal_id) == False:
            print("Failed to approve invoice: invoice not uploaded")
            return False
        columns = "internal_id, approved_by"
        values = f"{internal_id}, '{approved_by}'"
        if approval_date != None:
            columns += ", approval_date"
            values += f", '{approval_date}'"
        if approval_time != None:
            columns += ", approval_time"
            values += f", '{approval_time}'"
        return insert_into_table(connection, "approval_history", columns, values)
    else:
        print("Failed to approve invoice: user is not an approval manager")
        return False
    return False

def approve_invoices_by_vendor(connection, vendor_id, approved_by, approval_date = None, approval_time = None):
    if user_role_check(connection, approved_by, "approval_manager"):
        internal_ids = select_tuple_from_table(connection, "invoice", f"WHERE vendor_id = {vendor_id}")
        for internal_id in internal_ids:
            approve_invoice(connection, internal_id, approved_by, approval_date, approval_time)
        return True
    else:
        print("Failed to approve invoices: user is not an approval manager")
        return False
    return False

def approve_multiple_invoices(connection, internal_ids, approved_by, approval_date = None, approval_time = None):
    if user_role_check(connection, approved_by, "approval_manager"):
        for internal_id in internal_ids:
            approve_invoice(connection, internal_id, approved_by, approval_date, approval_time)
        return True
    else:
        print("Failed to approve invoices: user is not an approval manager")
        return False
    return False

def check_for_approval(connection, internal_id):
    try:
        select_value_from_table(connection, "approval_history", "internal_id", f"WHERE internal_id = {internal_id}", fetch_one = True, show_results = False)[0]
        return True
    except:
        return False

def get_approval_date(connection, internal_id):
    return select_value_from_table(connection, "approval_history", "approval_date", f"WHERE internal_id = {internal_id}", fetch_one = True, show_results = False)[0]

def get_approval_time(connection, internal_id):
    return select_value_from_table(connection, "approval_history", "approval_time", f"WHERE internal_id = {internal_id}", fetch_one = True, show_results = False)[0]

def get_approver_id(connection, internal_id):
    return select_value_from_table(connection, "approval_history", "approved_by", f"WHERE internal_id = {internal_id}", fetch_one = True, show_results = False)[0]

def get_approver_first_name(connection, internal_id):
    return select_value_from_table(connection, "user", "first_name", f"WHERE user_id = {get_approver_id(connection, internal_id)}", fetch_one = True, show_results = False)[0]

def get_approver_last_name(connection, internal_id):
    return select_value_from_table(connection, "user", "last_name", f"WHERE user_id = {get_approver_id(connection, internal_id)}", fetch_one = True, show_results = False)[0]

def get_approver_username(connection, internal_id):
    return select_value_from_table(connection, "user", "username", f"WHERE user_id = {get_approver_id(connection, internal_id)}", fetch_one = True, show_results = False)[0]

def get_approvals_by_user(connection, approved_by):
    return select_tuple_from_table(connection, "approval_history", f"WHERE approved_by = {approved_by}")

def get_approvals_by_date(connection, approval_date):
    return select_tuple_from_table(connection, "approval_history", f"WHERE approval_date = {approval_date}")

if __name__ == "__main__":
    connection = connect_to_db("database")
    table_name = "approval_history"
    columns = ("approval_id INTEGER PRIMARY KEY, "
               "internal_id INTEGER NOT NULL, "
               "approval_date DATE NOT NULL DEFAULT CURRENT_DATE, "
               "approval_time TIME NOT NULL DEFAULT CURRENT_TIME, "
               "approved_by INTEGER NOT NULL, "
               "FOREIGN KEY (internal_id) REFERENCES invoice(internal_id), "
               "FOREIGN KEY (approved_by) REFERENCES user(user_id)")

    #drop_table(connection, table_name)
    #create_table(connection, table_name, columns)

    #print(select_all_from_table(connection, table_name))
    user_id = get_user_id(connection, "user")
    admin_id = get_user_id(connection, "admin")
    print(approve_invoice(connection, 1, user_id))
    print(approve_invoice(connection, 1, admin_id))
    print(approve_invoice(connection, 2, user_id))
    print(approve_invoice(connection, 2, admin_id))

    print(f"Checking for approval: {check_for_approval(connection, 1)}")
    print(f"getting the approval date: {get_approval_date(connection, 1)}")
    print(f"getting the approval time: {get_approval_time(connection, 1)}")
    print(f"getting the approver's id: {get_approver_id(connection, 1)}")
    print(f"getting the approver's first name: {get_approver_first_name(connection, 1)}")
    print(f"getting the approver's last name: {get_approver_last_name(connection, 1)}")
    print(f"getting the approver's username: {get_approver_username(connection, 1)}")
    print(f"getting the approvals by user: {get_approvals_by_user(connection, user_id)}")
    print(f"getting the approvals by date: {get_approvals_by_date(connection, '2021-04-01')}")