from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app=Flask(__name__)

app.secret_key = 'a'

app.config['MYSQL_HOST'] = 'remotemysql.com'
app.config['MYSQL_USER'] = 'aW4y0436Cx'
app.config['MYSQL_PASSWORD'] = 'z89pJ54MBW'
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
            cursor.execute('INSERT INTO credentials VALUES (NULL, % s, % s, % s)', (username, email, password,))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)
@app.route('/login',methods =['GET', 'POST'])
def login():
    global userid
    msg = ''
    user= ''
    #count updation
    global activecases
    global newcases
    global deaths
    global recovered
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM updates WHERE id = 1')
    update = cursor.fetchone()
    print(update)
    activecases=update[1]
    newcases=update[2]
    deaths=update[3]
    recovered=update[4]
    ##############

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM credentials WHERE username = % s AND password = % s', (username, password), )
        account = cursor.fetchone()
        print(account)
        if account:
            session['loggedin'] = True
            session['id'] = account[0]
            userid = account[0]
            session['username'] = account[1]
            print(username)
            if re.match('admin',username):
                msg='welocome admin'
                return render_template('admin.html',msg=msg,activecases=activecases,newcases=newcases,deaths=deaths,recovered=recovered,user=username)
            else:
                msg = 'Logged in successfully !'
                user=username
                return render_template('dashboard.html', msg=msg,activecases=activecases,newcases=newcases,deaths=deaths,recovered=recovered,user=username)
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html',msg=msg)


@app.route('/dashboard')
def dashboard():
    global activecases
    global newcases
    global deaths
    global recovered
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM updates WHERE id = 1')
    update = cursor.fetchone()
    print(update)
    activecases = update[1]
    newcases = update[2]
    deaths = update[3]
    recovered = update[4]
    username= session["username"]
    return render_template('dashboard.html',user=username,activecases=activecases,newcases=newcases,deaths=deaths,recovered=recovered)
@app.route('/verify',methods =['GET', 'POST'])
def verify():
    msg = ''
    username = session["username"]
    if request.method == 'POST':
        state = request.form['state']
        district = request.form['district']
        area = request.form['area']

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM zones WHERE (district = %s AND area = %s)', (district,area,))
        zone = cursor.fetchone()
        print(zone)
        if  zone:
            msg = 'YOU ARE CURRENTLY IN A CONTAINMENT ZONE !'
            cursor.execute('INSERT INTO visited VALUES (NULL, % s, % s, % s, % s)', (username,state, district, area,))
            mysql.connection.commit()
        else:
            msg = 'YOU ARE CURRENTLY NOT IN A CONTAINMENT ZONE!'
    elif request.method == 'POST':
        msg = 'Please enter a zone !'
    return render_template('verify.html',user=username,msg=msg)
@app.route('/visitedzones')
def visitedzones():
    username = session["username"]
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM visited WHERE username = % s ', (username,))
    visited = cursor.fetchone()
    print(visited)
    if visited:
        visitedzones=[visited[0],visited[2],visited[3],visited[4]]
    else:
        visitedzones="YOU HAVE NOT VISITED ANY CONTAINMENT ZONE"
    return render_template('visitedzones.html', user=username, visitedzones=visitedzones)

@app.route('/countupdate',methods =['GET', 'POST'])
def countupdate():
    username = session["username"]
    if request.method == 'POST':
        activecases = request.form['activecases']
        newcases = request.form['newcases']
        deaths = request.form['deaths']
        recovered = request.form['recovered']
        cursor = mysql.connection.cursor()
        cursor.execute('UPDATE updates SET activecases = %s, newcases = %s, deaths = %s, recovered = %s WHERE id = 1',(activecases,newcases,deaths,recovered))
        mysql.connection.commit()
    return render_template('countupdate.html',user=username)
@app.route('/zoneupdate',methods =['GET', 'POST'])
def zoneupdate():
    msg = ''
    username=session["username"]
    if request.method == 'POST':
        state = request.form['state']
        district = request.form['district']
        area = request.form['area']

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM zones WHERE (district = %s AND area = %s)', (district,area,))
        zone = cursor.fetchone()
        print(zone)
        if  zone:
            msg = 'zone already exists !'
        else:
            cursor.execute('INSERT INTO zones VALUES (NULL, % s, % s, % s)', (state, district, area,))
            mysql.connection.commit()
            msg = 'zone has been added !'
    elif request.method == 'POST':
        msg = 'Please enter a zone !'
    return render_template('zoneupdate.html',msg=msg,user=username)

@app.route('/zonedeletion',methods =['GET', 'POST'])
def zonedeletion():
    msg=''
    username = session["username"]
    if request.method == 'POST':
        state = request.form['state']
        district = request.form['district']
        area = request.form['area']

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM zones WHERE (district = %s AND area = %s)', (district,area,))
        zone = cursor.fetchone()
        print(zone)
        if not zone:
            msg = 'zone does not exist !'
        else:
            cursor.execute('DELETE FROM zones  WHERE (district = %s AND area = %s)', (district,area,))
            mysql.connection.commit()
            msg = 'zone has been deleted !'
    elif request.method == 'POST':
        msg = 'Please enter a zone !'
    return render_template('zonedeletion.html',msg=msg,user=username )

@app.route('/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return render_template('homepage.html')




if __name__ == '__main__':
   app.run(host='0.0.0.0',debug = True,port = 8080)
