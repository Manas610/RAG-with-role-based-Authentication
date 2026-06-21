from app.Database import get_connection
from app.Auth import hash_password

conn = get_connection()
cursor = conn.cursor()
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    """
)


users = [
    (
        "manager",
        hash_password("manager123"),
        "manager"
    ),
    (
        "lead",
        hash_password("lead123"),
        "project_lead"
    ),
    (
        "employee",
        hash_password("employee123"),
        "employee"
    )
]


for user in users:

    try:
        cursor.execute(
            """
            INSERT INTO users(
                username,
                password,
                role
            ) VALUES (?, ?, ?)
            """,
            user
        )

    except:
        pass


conn.commit()
conn.close()

print("Database Initialized")