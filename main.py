from flask import Flask, render_template, request, flash, redirect, url_for, session
import sqlite3
import random
import string
import sys
import timeago
from datetime import datetime
from pydb import fetchEvents, fetchUser, fetchFriendsdata, fetchFriends, fetchFriendRequests, fetchTweets, updateNumEvents, updateNumFriends, updateNumTweets, checkRequestExists, unfollowUser

letters = string.ascii_lowercase

def get_random_string():
    result = ''.join(random.choice(letters) for i in range(15))
    return result

def get_random_number():
    return random.randint(0, 99999999999)

app = Flask(__name__)
app.secret_key = 'kiminonawa'

@app.route('/')
def index():
    return redirect(url_for('home'))


@app.route('/login', methods = ['GET', 'POST'])
def login():
    if 'id' in session:
        return redirect(url_for('home'))
    error = None
    if(request.method == 'POST'):
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect('database.db') as con:
            cur = con.cursor()
            cur.execute('SELECT * from Users WHERE username = ?', [username,])
            details = cur.fetchall()
            if(len(details) == 0):
                error = "wrong credentials"
            elif(details[0][2] == password):
                session['id'] = details[0][3]
                session['username'] = details[0][0]
                return redirect(url_for('home'))
            else:
                error = "wrong credentials"
        return render_template('login.html', error = error)
    return render_template('login.html', error = error)

@app.route('/signup', methods = ['POST', 'GET'])
def signup():
    if 'id' in session:
        return redirect(url_for('home'))
    error = None
    if(request.method == 'POST'):
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confpass = request.form['confpass']
        if(password != confpass):
            error = "Passwords doesn't match"
        else:
            Id = get_random_string()
            con = sqlite3.connect('database.db')
            cur = con.cursor()
            cur.execute("SELECT * from Users WHERE username = ?", (username,))
            details = cur.fetchall()
            if(len(details) == 0):
                con.execute("INSERT INTO Users (username, email, password, id) VALUES (?, ?, ?, ?)", (username, email, password, Id))
                con.commit()
                con.close()
                session['id'] = Id
                session['username'] = username
                return redirect(url_for('home'))
            else:
                error = "Username taken"
    return render_template('signup.html', error = error)

@app.route('/home')
def home():
    if 'id' in session:
        return render_template('home.html')
    else:
        return redirect(url_for('login'))

@app.route('/events', methods = ['POST', 'GET'])
def events():
    if(request.method == 'POST'):
        username = session['username']
        eventname = request.form['eventname']
        date = request.form['dateinput']
        stime = request.form['stime']
        etime = request.form['etime']
        descrip = request.form['description']
        eventId = get_random_number()
        con = sqlite3.connect('database.db')
        con.execute("INSERT INTO events (username, eventName, date, startTime, endTime, description, eventId) VALUES (?, ?, ?, ?, ?, ?, ?)", (username, eventname, date, stime, etime, descrip, eventId))
        con.commit()
        con.close()
        return redirect(url_for('events'))
    if 'id' in session:
        events=fetchEvents(session['username'])
        frndRequests = fetchFriendRequests(session['username'])
        if(len(frndRequests) > 0):
            return render_template('events.html', username = session['username'], e=events, no=len(events), tempdate="1234", alrert = len(frndRequests))
        return render_template('events.html', username = session['username'], e=events, no=len(events), tempdate="1234")
    else:
        return redirect('login')

@app.route('/logout')
def logout():
    session.pop('id', None)
    return redirect(url_for('login'))

@app.route('/editevent', methods = ['POST', 'GET'])
def editEvent():
    if request.method == 'POST':
        username = session['username']
        eventname = request.form['eventname']
        date = request.form['dateinput']
        stime = request.form['stime']
        etime = request.form['etime']
        descrip = request.form['description']
        eventId = request.form['eventId']
        con = sqlite3.connect('database.db')
        con.execute('''UPDATE events SET username = ?,
                                         eventName = ?,
                                         date = ?,
                                         startTime = ?,
                                         endTime = ?,
                                         description = ?
                                         WHERE eventId = ?''', (username, eventname, date, stime, etime, descrip, eventId))
        con.commit()
        con.close()
        return redirect(url_for('events'))
    return redirect(url_for('events'))

@app.route('/update', methods = ['POST', 'GET'])
def update():
    if request.method == 'POST':
        eventId = request.form['eventId']
        con = sqlite3.connect('database.db')
        cur = con.cursor()
        cur.execute("SELECT * FROM events WHERE eventId = ?", (eventId,))
        data = cur.fetchall()
        con.close()
        return render_template("editEvent.html", data = data[0])
    return redirect('home')

@app.route('/delete', methods = ['POST', 'GET'])
def delete():
    if request.method == 'POST':
        eventId = request.form['eventId']
        con = sqlite3.connect('database.db')
        con.execute("DELETE FROM events WHERE eventId = ?", (eventId,))
        con.commit()
        con.close()
        return redirect(url_for('events'))
    redirect(url_for('events'))

@app.route('/profile')
def profile():
    if 'id' in session:
        username = session['username']
        updateNumEvents(username)
        updateNumFriends(username)
        updateNumTweets(username)
        data = fetchUser(session['username'])
        frndRequests = fetchFriendRequests(session['username'])
        if(len(frndRequests) > 0):
            return render_template('profile.html', username = session['username'], data = data[0], alert = len(frndRequests))
        return render_template('profile.html', username = session['username'], data = data[0])
    return redirect('home')

@app.route('/friends', methods = ['POST', 'GET'])
def friends():
    if request.method == 'POST':
        username = session['username']
        suser = request.form['suser']
        suserData = fetchUser(suser)
        friends = fetchFriends(username)
        friendsdata = fetchFriendsdata(username)
        frndRequests = fetchFriendRequests(username)
        if(checkRequestExists(username, suser)):
            if(len(frndRequests) > 0):
                return render_template('friends.html', msg = "Request already sent to user", friends = friendsdata, alert = len(frndRequests))
            return render_template('friends.html', msg = "Request already sent to user", friends = friendsdata)
        if(len(suserData) == 0):
            if(len(frndRequests) > 0):
                return render_template('friends.html', msg = "No such user found", friends = friendsdata, alert = len(frndRequests))
            return render_template('friends.html', msg = "No such user found", friends = friendsdata)
        else:
            if suserData[0][0] in friends:
                if(len(frndRequests) > 0):
                    return render_template('friends.html', msg = "User already your friend.", friends = friendsdata, alert = len(frndRequests))
                return render_template('friends.html', msg = "User already your friend.", friends = friendsdata)
            elif suserData[0][0] == username:
                if(len(frndRequests) > 0):
                    return render_template('friends.html', msg = "Find a friend other than yourself.", friends = friendsdata, alert = len(frndRequests))
                return render_template('friends.html', msg = "Find a friend other than yourself.", friends = friendsdata)
            else:
                if(len(frndRequests) > 0):
                    return render_template('friends.html', msg = "User found" , sfriend = suserData, friends = friendsdata, alert = len(frndRequests))
                return render_template('friends.html', msg = "User found" , sfriend = suserData, friends = friendsdata)
    if 'id' in session:
        username = session['username']
        friendsdata = fetchFriendsdata(username)
        frndRequests = fetchFriendRequests(username)
        if(len(frndRequests) > 0):
            return render_template('friends.html', msg = "Search for friends to connect with them.", friends = friendsdata, alert = len(frndRequests))
        return render_template('friends.html', msg = "Search for friends to connect with them.", friends = friendsdata)   
    return render_template('friends.html', msg = "Search for friends to connect with them.")

@app.route('/notifications')
def notifications():
    if 'id' in session:
        username = session['username']
        friendRequests = fetchFriendRequests(username)
        frndData = []
        for i in friendRequests:
            row = fetchUser(i[0])
            frndData.append(row)
        if(len(frndData) == 0):
            return render_template('notifications.html', msg = "No new friend request")
        return render_template('notifications.html', frndData = frndData, alert = len(friendRequests))

@app.route('/sendfrequest', methods = ['POST'])
def sendfrequest():
    if request.method == 'POST':
        username = session['username']
        fusername = request.form['fuser']
        con = sqlite3.connect('database.db')
        con.execute("INSERT INTO frequest (fromUser, toUser) VALUES (?, ?)", (username, fusername))
        con.commit()
        con.close()
        return redirect(url_for('friends'))

@app.route('/accept', methods = ['POST'])
def accept():
    if request.method == 'POST':
        username = session['username']
        fusername = request.form['fuser']
        userFriends = fetchFriends(username)
        fuserFriends = fetchFriends(fusername)
        userFriends.append(fusername)
        fuserFriends.append(username)
        new_u = ','.join(userFriends)
        new_f = ','.join(fuserFriends)
        con = sqlite3.connect('database.db')
        con.execute("UPDATE Users SET friends = ? WHERE username = ?", (new_u, username))
        con.execute("UPDATE Users SET friends = ? WHERE username = ?", (new_f, fusername))
        con.execute("DELETE FROM frequest WHERE fromUser = ? AND toUser = ?", (fusername, username))
        con.commit()
        con.close()
        return redirect(url_for('notifications'))

@app.route('/decline', methods = ['POST'])
def decline():
    if request.method == 'POST':
        username = session['username']
        fusername = request.form['fuser']
        con = sqlite3.connect('database.db')
        con.execute("DELETE FROM frequest WHERE fromUser = ? AND toUser = ?", (fusername, username))
        con.commit()
        con.close()
        return redirect(url_for('notifications'))

@app.route('/tweets', methods = ['POST', 'GET'])
def tweets():
    if request.method == 'POST':
        username = session['username']
        message = request.form['message']
        posttime = str(datetime.now())[0:19]
        Id = random.randint(0, 9999999999)
        con = sqlite3.connect('database.db')
        con.execute("INSERT INTO tweets (username, message, postTime, Id) VALUES (?, ?, ?, ?)", (username, message, posttime, Id))
        con.commit()
        con.close()
    if 'id' in session:
        username = session['username']
        frndRequests = fetchFriendRequests(username)
        tweets = []
        friends = fetchFriends(username)
        friends.append(username)
        now = str(datetime.now())[0:19]
        for i in friends:
            row = fetchTweets(i)
            for j in row:
                j = list(j)
                ago = timeago.format(j[2], now)
                j.append(ago)
                j = [j[2]] + j
                tweets.append(j)
        tweets.sort(reverse = True)
        if(len(frndRequests) > 0):
            return render_template('tweets.html', tweets = tweets, alert = len(frndRequests))
        return render_template('tweets.html', tweets = tweets)
    return redirect(url_for('home'))

@app.route('/share', methods = ['POST'])
def share():
    if request.method == 'POST':
        eventId = request.form['eventId']
        con = sqlite3.connect('database.db')
        cur = con.cursor()
        cur.execute("SELECT * FROM events WHERE eventId = ?", (eventId,))
        data = cur.fetchall()
        con.close()
        friends = fetchFriends(session['username'])
        if(len(friends) == 0):
            return render_template("share.html", data = data[0], msg = "You have no friends yet, connet with friends to share")
        return render_template("share.html", data = data[0], friends = friends)
    return redirect('home')

@app.route('/shareevent', methods = ['POST'])
def shareevent():
    if request.method == 'POST':
        username = request.form['username']
        eventname = request.form['eventname']
        date = request.form['dateinput']
        stime = request.form['stime']
        etime = request.form['etime']
        descrip = request.form['description']
        eventId = get_random_number()
        con = sqlite3.connect('database.db')
        con.execute("INSERT INTO events (username, eventName, date, startTime, endTime, description, eventId) VALUES (?, ?, ?, ?, ?, ?, ?)", (username, eventname, date, stime, etime, descrip, eventId))
        con.commit()
        con.close()
        return redirect(url_for('events'))

@app.route('/statusupdate', methods = ['POST', 'GET'])
def statusupdate():
    if request.method == "POST":
        username = session['username']
        status = request.form['status']
        con = sqlite3.connect('database.db')
        con.execute("UPDATE Users SET status = ? WHERE username = ?", (status, username))
        con.commit()
        con.close()
        return redirect(url_for('profile'))

@app.route('/unfollow', methods = ['POST'])
def unfollow():
    if request.method == 'POST':
        username = session['username']
        fusername = request.form['fuser']
        unfollowUser(username, fusername)
        return redirect(url_for('friends'))

if __name__ == '__main__':
    app.run(debug = True)