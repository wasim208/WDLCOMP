from flask import Flask, render_template, request, flash, redirect, url_for, session
import sqlite3
import random
import string
import sys

letters = string.ascii_lowercase

def get_random_string():
    result = ''.join(random.choice(letters) for i in range(15))
    return result

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

@app.route('/home', methods = ['POST', 'GET'])
def home():
    if 'id' in session:
        return render_template('home.html', username = session['username'])
    else:
        return redirect('login')

@app.route('/logout')
def logout():
    session.pop('id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug = True)