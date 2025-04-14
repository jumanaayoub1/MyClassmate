import sqlite3
import db  # your db.py file


with sqlite3.connect("database.db") as conn:
    conn.row_factory = sqlite3.Row

    # Create tables
    db._make_tables(conn)

    # Add two users with unique, unused IDs
    db.insert_user(conn, user_id=301, user_password="pass123", username="alice", privacy="public", major="CMPE")
    db.insert_user(conn, user_id=302, user_password="pass456", username="bob", privacy="private", major="EE")

    # Enroll user 301 in a class
    class_id = db.possibly_create_class_and_get_id(conn, "CMPE", 131, 1)
    db.enroll_in_class(conn, user_id=301, class_id=class_id)

    # Make them friends
    db.add_friend(conn, 301, 302)
    db.accept_friend(conn, 301, 302)

    # Now test the get_user_info function
    user_info = db.get_user_info(conn, target_id=301, source_id=302)

    # Print out what you got
    if user_info:
        print("User Info:")
        print(dict(user_info))  # basic info
        print("Classes:")
        print(user_info["classes"])  # should list classes
    else:
        print("No user found or no access!")

