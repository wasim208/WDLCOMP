import sqlite3
def fetchEvents(username):
    conn = sqlite3.connect('database.db')
    print("Opened database successfully")
    cur = conn.cursor()
    cur.execute("SELECT * from events WHERE username=:user order by date(date)asc,startTime asc;",{'user':username})
    row = cur.fetchall()
    print(row)
    return row