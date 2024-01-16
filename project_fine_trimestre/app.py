from flask import Flask, render_template, request, redirect, url_for
import sqlite3 as sql
import hashlib
import AlphaBot as ab
from time import sleep
from random import randint

app = Flask(__name__)

susina =ab.AlphaBot()
moves = {'f': susina.forward, 'b': susina.backward, 'r': susina.right, 'l': susina.left}

secretNum = randint(0, 1234567890)

def validate(username, password):
    db = sql.connect('db_TPSIT_robot.db')
    cur = db.cursor()
    res = cur.execute(f"SELECT Username, Psw FROM Users WHERE Username = '{username}' AND Psw = '{password}'").fetchall()
    cur.close()
    db.close()
    return len(res) > 0


def getSpecialCommands():
    db = sql.connect('dbRobot')
    cur = db.cursor()
    res = cur.execute('SELECT * FROM movements').fetchall()
    cur.close()
    db.close()
    print(res)
    return res


commands = getSpecialCommands()


@app.route('/')
def index():
    return render_template('login.html', error=None)


@app.route('/login', methods=['POST'])
def login():
    username = request.form['Username']
    password = request.form['Psw']
    password = hashlib.md5(password.encode()).hexdigest()

    if validate(username, password):
        secretNum = randint(0, 1234567890)
        return redirect(url_for('secret'))
    else:
        return render_template('login.html', error=True)


@app.route('/move', methods=['POST'])
def move():
    command = request.form.get('command')
    for com in commands:
        if command == com[1]:
            passaggi = com[2].split(';')
            for pas in passaggi:
                lett = pas[0]
                time = float(pas[1:])

                moves[lett]()
                sleep(time)
                susina.stop()
            
            secretNum = randint(0, 1234567890)
            return redirect(url_for('secret'))

    moves[request.form.get('command')]()
    sleep(0.5)
    susina.stop()

    secretNum = randint(0, 1234567890)
    return redirect(url_for('secret'))


@app.route(f'/{secretNum}')
def secret():
    return render_template('index.html', commands=commands)


app.run(host='0.0.0.0', debug=True)
