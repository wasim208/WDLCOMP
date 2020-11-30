import sqlite3
def fetchEvents(username):
    conn = sqlite3.connect('database.db')
    print("Opened database successfully")
    cur = conn.cursor()
    cur.execute("SELECT * from events WHERE username=:user order by date(date)asc,startTime asc;",{'user':username})
    row = cur.fetchall()
    conn.close()
    print(row)
    return row

def fetchUser(username):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM Users WHERE username = ?", (username,))
    row = cur.fetchall()
    conn.close()
    print(row)
    return row

def fetchFriends(username):
    data = fetchUser(username)
    friends = []
    if(data[0][8] != None):
        friends = data[0][8].split(',')
    return friends

def fetchFriendsdata(username):
    friends = fetchFriends(username)
    friendsdata = []
    for i in friends:
        frd = fetchUser(i)
        friendsdata.append(frd)
    return friendsdata

def fetchFriendRequests(username):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM frequest WHERE toUser = ?", (username, ))
    row = cur.fetchall()
    con.close()
    return row

def fetchTweets(username):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM tweets WHERE username = ?", (username,))
    row = cur.fetchall()
    con.close()
    return row

def unfollowUser(username, fusername):
    con = sqlite3.connect('database.db')
    friends = fetchFriends(username)
    friends.remove(fusername)
    if len(friends) == 0:
        con.execute("UPDATE Users SET friends = NULL WHERE username = ?", (username,))
    else:
        new_frnds = ','.join(friends)
        con.execute("UPDATE Users SET friends = ? WHERE username = ?", (new_frnds, username))
    friends = fetchFriends(fusername)
    friends.remove(username)
    if len(friends) == 0:
        con.execute("UPDATE Users SET friends = NULL WHERE username = ?", (fusername,))
    else:
        new_frnds = ','.join(friends)
        con.execute("UPDATE Users SET friends = ? WHERE username = ?", (new_frnds, fusername))
    con.commit()
    con.close()
    

def checkRequestExists(username, fusername):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM frequest WHERE fromUser = ? AND toUser = ?", (username, fusername))
    row = cur.fetchall()
    if(len(row) == 0):
        return 0
    else:
        return 1

def updateNumEvents(username):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM events WHERE username = ?", (username,))
    row = cur.fetchall()
    number = len(row)
    con.execute("UPDATE Users SET numEvents = ? WHERE username = ?", (number, username))
    con.commit()
    con.close()

def updateNumTweets(username):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM tweets WHERE username = ?", (username,))
    row = cur.fetchall()
    number = len(row)
    con.execute("UPDATE Users SET numTweets = ? WHERE username = ?", (number, username))
    con.commit()
    con.close()

def updateNumFriends(username):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM Users WHERE username = ?", (username,))
    row = cur.fetchall()
    number = 0
    if(row[0][8] != None):
        l = row[0][8].split(',')
        number = len(l)
    con.execute("UPDATE Users SET numFriends = ? WHERE username = ?", (number, username))
    con.commit()
    con.close()