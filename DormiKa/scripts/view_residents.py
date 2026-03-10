import sqlite3

conn = sqlite3.connect(r"C:\Users\James\Desktop\Ducky-Dicka\main\residents.db")
cursor = conn.cursor()

# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(cursor.fetchall())

# View all rows in residents table
cursor.execute("SELECT * FROM residents;")
rows = cursor.fetchall()
for row in rows:
    print(row)

conn.close()