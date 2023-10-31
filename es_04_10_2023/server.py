import AlphaBot as ab
import socket as sck
from threading import Thread
from time import sleep
import RPi.GPIO as GPIO

DR = 16
DL = 19

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

        emergenza = False
        global IN_EMERGENZA
        global IN_AZIONE
        global susina

        try:
            while True:
                if not IN_AZIONE or IN_EMERGENZA or IS_BACK:
                    continue

                DR_status = GPIO.input(DR)
                DL_status = GPIO.input(DL)
                if((DL_status == 1) and (DR_status == 0) and not IN_EMERGENZA):
                    susina.stop()
                    IN_EMERGENZA = True
                    conn.sendall('EMERGENZA: gira a sinistra'.encode())
                elif((DL_status == 0) and (DR_status == 1) and not IN_EMERGENZA):
                    susina.stop()                
                    IN_EMERGENZA = True
                    conn.sendall('EMERGENZA: gira a destra'.encode())
                elif((DL_status == 0) and (DR_status == 0) and not IN_EMERGENZA):
                    susina.stop()                
                    IN_EMERGENZA = True
                    conn.sendall('EMERGENZA: vai indietro'.encode())
                                    
        except KeyboardInterrupt:
            GPIO.cleanup()

SEP = ';'

susina = ab.AlphaBot()

socket = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
socket.bind(('0.0.0.0', 8888))

socket.listen()
conn, addr = socket.accept()

move = {'f': susina.forward, 'b': susina.backward, 'l': susina.right, 'r': susina.left}

s = Sensori(conn)
s.start()
while True:
    data = conn.recv(4096).decode()
    if SEP not in data:
        conn.sendall(f'il messaggio inviato deve contenere il carattere separatore {SEP}'.encode())
        continue

    datas = data.split(';')
    if datas[0].lower() in move:
        if datas[0].lower() == 'b':
            IS_BACK = True

        move[datas[0].lower()]()
        IN_AZIONE = True
        sleep(float(datas[1]))
        if not IN_EMERGENZA:
            susina.stop()
            conn.sendall('comando fatto'.encode())
        IN_EMERGENZA = False
        IN_AZIONE = False
        IS_BACK = False
    else:
        conn.sendall(f"il primo parametro passato deve essere uno tra {'-'.join(list(move.keys()))}".encode())
