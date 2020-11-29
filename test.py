import sqlite3
import timeago
from datetime import datetime
import string

con = sqlite3.connect('database.db')
cur = con.cursor()

username = 'light'
message = "I will become the God of the new world"
ptime = str(datetime.now())[0:19]



cur.execute("SELECT * FROM tweets")
#con.execute("INSERT INTO tweets (username, message, postTime) VALUES (?, ?, ?)", (username, message, ptime))
# cur.execute("DELETE * Users WHERE username = ?", (username))
row = cur.fetchall()
posttime = row[0][2]
posttime = posttime[0:19]
now = datetime.now()

# print(type(row[0][2]))
# print(type(str(now)))

now_str = str(now)[0:19]
past = timeago.format(posttime, now_str)
print(past)
# print(now_str)
# print(posttime)



con.commit()
con.close()

# print(row)