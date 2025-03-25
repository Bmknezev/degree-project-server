from database.db_interaction_functions import *


def create_status(connection):
    # create a view called status
    query = "CREATE VIEW status AS "\
                "SELECT i.internal_id, "\
                    "CASE "\
                        "WHEN EXISTS (SELECT 1 FROM payment_history WHERE internal_id = i.internal_id) THEN 'paid' "\
                        "WHEN EXISTS (SELECT 1 FROM approval_history WHERE internal_id = i.internal_id) THEN 'awaiting payment' "\
                        "ELSE 'awaiting approval' "\
                    "END AS status "\
                "FROM invoice i"

    return execute_query(connection, query)

def drop_status(connection):
    # drop the status view
    query = "DROP VIEW status"

    return execute_query(connection, query)

def create_date_edited(connection):
        # create a view called date_edited
    query = "CREATE VIEW date_edited AS "\
                "SELECT i.internal_id, "\
                    "CASE "\
                        "WHEN EXISTS (SELECT 1 FROM payment_history WHERE internal_id = i.internal_id) "\
                            "THEN (SELECT payment_date FROM payment_history WHERE internal_id = i.internal_id) "\
                        "WHEN EXISTS (SELECT 1 FROM approval_history WHERE internal_id = i.internal_id) "\
                            "THEN (SELECT approval_date FROM approval_history WHERE internal_id = i.internal_id) "\
                        "ELSE (SELECT upload_date FROM upload_history WHERE internal_id = i.internal_id) "\
                    "END AS date_edited "\
                "FROM invoice i"

    return execute_query(connection, query)

def drop_date_edited(connection):
    # drop the date_edited view
    query = "DROP VIEW date_edited"

    return execute_query(connection, query)

if __name__ == "__main__":
    connection = connect_to_db("database")

    print(drop_status(connection))
    print(create_status(connection))
    print(select_all_from_table(connection, "status"))

    print(drop_date_edited(connection))
    print(create_date_edited(connection))
    print(select_all_from_table(connection, "date_edited"))



