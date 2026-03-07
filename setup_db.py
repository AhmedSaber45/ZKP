import sqlite3

# Create database connection
conn = sqlite3.connect("database/zkp_auth.db")

# Execute schema.sql to create tables
with open("database/schema.sql") as f:
    conn.executescript(f.read())

conn.commit()
conn.close()
print("Database initialized successfully!")