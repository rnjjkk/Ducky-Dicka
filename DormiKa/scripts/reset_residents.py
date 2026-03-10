import sqlite3

conn = sqlite3.connect(r"C:\Users\James\Desktop\Ducky-Dicka\main\residents.db")
cursor = conn.cursor()

cursor.execute("DELETE FROM residents;")

cursor.execute("DELETE FROM sqlite_sequence WHERE name='residents';")

conn.commit()
conn.close()

print("Residents table cleared and ID cunter reset.")