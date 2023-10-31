import AlphaBot as ab
import socket as sck
import sqlite3 as sql
from time import sleep
import RPi.GPIO as GPIO
from threading import Thread, Lock

DR = 16
DL = 19
susina = ab.AlphaBot()
#mutex = Lock()

IN_EMERGENZA = False
IN_AZIONE = False
IS_BACK = False

class Sensori(Thread):
    def __init__(self, conn):
        Thread.__init__(self)
        self.conn = conn

    def run(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(DR,GPIO.IN,GPIO.PUD_UP)
        GPIO.setup(DL,GPIO.IN,GPIO.PUD_UP)
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(DR,GPIO.IN,GPIO.PUD_UP)
        GPIO.setup(DL,GPIO.IN,GPIO.PUD_UP)

        global IN_EMERGENZA
        global IN_AZIONE
        global susina

        try:
            while True:
                #mutex.acquire()
                if not IN_AZIONE or IN_EMERGENZA or IS_BACK:
                    continue
                #mutex.release()

                DR_status = GPIO.input(DR)
                DL_status = GPIO.input(DL)
                
                if ((DL_status == 0) or (DR_status == 0)) and not IN_EMERGENZA:
                    #mutex.acquire()
                    IN_EMERGENZA = True
                    #mutex.release()
                    susina.stop()
                    
                    if((DL_status == 1) and (DR_status == 0)):
                        conn.sendall('EMERGENZA: gira a sinistra'.encode())
                    elif((DL_status == 0) and (DR_status == 1)):
                        conn.sendall('EMERGENZA: gira a destra'.encode())
                    elif((DL_status == 0) and (DR_status == 0)):
                        conn.sendall('EMERGENZA: vai indietro'.encode())
                                    
        except KeyboardInterrupt:
            GPIO.cleanup()

con = sql.connect('dbRobot')

cur = con.cursor()
res = cur.execute('SELECT shortcut FROM movements')
shortcuts = [t[0] for t in res.fetchall()]

SEP = ';'
socket = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
socket.bind(('0.0.0.0', 8800))

socket.listen()
conn, addr = socket.accept()

move = {'f': susina.forward, 'b': susina.backward, 'r': susina.right, 'l': susina.left}

s = Sensori(conn)
s.start()

try:
    while True:
        data = conn.recv(4096).decode()
        if data in shortcuts:
            res = cur.execute(f"SELECT mov_sequence FROM movements WHERE shortcut = '{data}'")
            res = res.fetchone()
            sequence = res[0].split(';')
            for seq in sequence:
                if IN_EMERGENZA:
                    break
                #mutex.acquire()
                IN_AZIONE = True
                command = seq[0].lower()
                if command == 'b':
                    IS_BACK = True

                time = float(seq[1:])
                move[command]()
                #mutex.release()
                
                sleep(time)
                
                #mutex.acquire()
                IS_BACK = False
                if IN_EMERGENZA:
                    break
                else:
                    susina.stop()
                IN_AZIONE = False
                #mutex.release()



            if not IN_EMERGENZA:      
                conn.sendall('comando fatto pt2'.encode())
        else:
            if SEP not in data:
                conn.sendall(f'il messaggio inviato deve contenere il carattere separatore {SEP}'.encode())
                continue

            datas = data.split(SEP)
            if datas[0].lower() in move:
                #mutex.acquire()
                if datas[0].lower() == 'b':
                    IS_BACK = True
                IN_AZIONE = True
                #mutex.release()

                move[datas[0].lower()]()
                sleep(float(datas[1]))

                if not IN_EMERGENZA:
                    susina.stop()
                    conn.sendall('comando fatto'.encode())
            else:
                conn.sendall('comando non fatto'.encode())

        #mutex.acquire()
        IN_EMERGENZA = False
        IN_AZIONE = False
        IS_BACK = False
        #mutex.release()
except:
    socket.close()
    con.close()
