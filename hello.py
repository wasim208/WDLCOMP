from flask import Flask, render_template, request, flash, redirect, url_for
import sqlite3
import random
import string
import sys

letters = string.ascii_lowercase

def get_random_string():
    result = ''.join(random.choice(letters) for i in range(15))
    return result

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello Mars'

@app.route('/login', methods = ['GET', 'POST'])
def login():
    error = None
    if(request.method == 'POST'):
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect('database.db') as con:
            cur = con.cursor()
            cur.execute('SELECT * from Users WHERE username = ?', [username,])
            details = cur.fetchall()
            print(details, file=sys.stdout)
            if(details[0][2] == password):
                return redirect(url_for('home'))
            else:
                error = "wrong credentials"
        return render_template('login.html', error = error)
    return render_template('login.html', error = error)

@app.route('/signup', methods = ['POST', 'GET'])
def signup():
    error = None
    if(request.method == 'POST'):
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        Id = get_random_string()
        with sqlite3.connect('database.db') as con:
            con.execute("INSERT INTO Users (username, email, password, id) VALUES (?, ?, ?, ?)", (username, email, password, Id))
            con.commit()
            con.close()
            return redirect(url_for('home'))
    return render_template('signup.html', errors = error)

@app.route('/home')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.debug = True
    app.run()
    app.run(debug = True)