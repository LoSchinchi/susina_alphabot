# Importazioni necessarie
from flask import Flask, render_template, make_response, request
import sqlite3 as sql
import hashlib
import AlphaBot as ab
from time import sleep
from random import randint
from datetime import date, datetime

# Inizializzazione dell'app Flask
app = Flask(__name__)

# Inizializzazione di un oggetto AlphaBot per controllare il robot
susina = ab.AlphaBot()

# Mappatura dei comandi ai metodi corrispondenti di AlphaBot
moves = {'f': susina.forward, 'b': susina.backward, 'r': susina.right, 'l': susina.left}

# Funzione per validare le credenziali dell'utente nel database
def validate(username, password):
    db = sql.connect('db_TPSIT_robot.db')
    cur = db.cursor()
    res = cur.execute(f"SELECT Username, Psw FROM Users WHERE Username = '{username}' AND Psw = '{password}'").fetchall()
    cur.close()
    db.close()
    return len(res) > 0

# Funzione per ottenere i comandi speciali dal database
def getSpecialCommands():
    db = sql.connect('db_TPSIT_robot.db')
    cur = db.cursor()
    res = cur.execute('SELECT * FROM movements').fetchall()
    cur.close()
    db.close()
    print(res)
    return res

# Funzione per inserire un comando nella cronologia nel database
def insertInHistory(command, user):
    today = date.today()

    db = sql.connect('db_TPSIT_robot.db')
    cur = db.cursor()
    res  = cur.execute(f"SELECT Id FROM Users WHERE Username='{user}'").fetchone()[0]
    time = datetime.now().strftime('%H:%M:%S')
    print(res, command)
    cur.execute(f"INSERT INTO History (Comando, Id_User, Data, Ora) VALUES ('{command}', {res}, '{today}', '{time}')")
    db.commit()
    cur.close()
    db.close

# Ottenimento dei comandi speciali (shortcuts)
commands = getSpecialCommands()

# Definizione della route principale
@app.route('/')
def index():
    return render_template('login.html', error=None)

# Gestione del login
@app.route('/login', methods=['POST'])
def login():
    username = request.form['Username']
    password = request.form['Psw']
    password = hashlib.md5(password.encode()).hexdigest() # hash della password
    
    if validate(username, password):
        resp = make_response(render_template('index.html', commands=commands))
        resp.set_cookie('username', username)
        return resp
    else:
        return render_template('login.html', error=True)

# Gestione dei comandi di movimento
@app.route('/move', methods=['POST'])
def move():
    # controllo se l'utente è loggato
    if not request.cookies.get('username'):
        return render_template('login.html')

    command = request.form.get('command')
    for com in commands:
        # controllo se è una shortcut
        if command == com[1]:
            passaggi = com[2].split(';')
            for pas in passaggi:
                lett = pas[0]
                time = float(pas[1:])

                moves[lett]()
                sleep(time)
                susina.stop()
            
            resp = make_response(render_template('index.html', commands=commands))
            resp.set_cookie('username', request.cookies.get('username'))
            
            insertInHistory(com[2], request.cookies.get('username'))
            return resp

    # se è qui non è una shortcut
    moves[request.form.get('command')]()
    sleep(0.5)
    susina.stop()

    #rimando la pagina riscrivendo anche il cookie
    resp = make_response(render_template('index.html', commands=commands))
    resp.set_cookie('username', request.cookies.get('username'))
    
    insertInHistory(request.form.get('command'), request.cookies.get('username'))
    return resp

"""
@app.route(f'/{secretNum}')
def secret():
    return render_template('index.html', commands=commands)
"""

# Avvio dell'app Flask
app.run(host='0.0.0.0', debug=True)

