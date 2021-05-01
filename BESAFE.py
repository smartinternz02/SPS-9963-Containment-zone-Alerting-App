from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors

app=Flask(__name__)

app.secret_key = 'a'

app.config['MYSQL_HOST'] = 'remotemysql.com'
app.config['MYSQL_USER'] = 'aW4y0436Cx'
app.config['MYSQL_PASSWORD'] = 'z27pJ54MBW'
app.config['MYSQL_DB'] = 'aW4y0436Cx'
mysql = MySQL(app)


@app.route('/')

def homer():
    return render_template('homepage.html')
@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM credentials WHERE username = % s', (username,))
        account = cursor.fetchone()
        print(account)
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'name must contain only characters and numbers !'
        else:
            cursor.execute('INSERT INTO credentials VALUES (NULL, % s, % s, % s)', (username, email, password))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)
@app.route('/login',methods =['GET', 'POST'])
def login():
    return render_template('login.html')
if __name__ == '__main__':
   app.run(debug = True)