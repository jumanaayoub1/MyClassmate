import sqlite3
import db

def test_remove_class():
    with sqlite3.connect("database.db") as conn:
        conn.row_factory = sqlite3.Row

        print("🚧 Creating tables...")
        db._make_tables(conn)

        print("👤 Inserting test user...")
        db.insert_user(conn, 999, "testpass", username="tester", privacy="public", major="CMPE")

        print("📚 Creating test class...")
        class_id = db.possibly_create_class_and_get_id(conn, "CMPE", 131, 1)

        print("✅ Enrolling user into class...")
        db.enroll_in_class(conn, 999, class_id)

        before = conn.execute(
            "SELECT * FROM users_classes_junction WHERE user_id = 999"
        ).fetchall()
        print("📌 Before removal:", [dict(row) for row in before])

        print("❌ Removing class...")
        db.remove_class(conn, 999, class_id)

        after = conn.execute(
            "SELECT * FROM users_classes_junction WHERE user_id = 999"
        ).fetchall()
        print("📌 After removal:", [dict(row) for row in after])

test_remove_class()