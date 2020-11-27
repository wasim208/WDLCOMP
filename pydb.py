import sqlite3

conn = sqlite3.connect('database.db')
print("Opened database successfully")

cur = conn.cursor()

usrname = "light"

cur.execute("SELECT * from Users WHERE username = ?", (usrname,))

row = cur.fetchall()

print(row[0][2])