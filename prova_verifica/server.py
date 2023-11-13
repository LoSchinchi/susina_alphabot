
import socket as sck
import sqlite3 as sql
from threading import Thread

SEP = ';'
MESSAGE_REQUEST_NAME_FILE = 'filename'
MESSAGE_REQUEST_N_FRAMM = 'nframm'
MESSAGE_REQUEST_IP = 'getip'
MESSAGE_REQUEST_EACH_IP = 'eachip'

class Client(Thread):
    def __init__(self, conn: sck.socket):
        Thread.__init__(self)
        self.conn = conn

    def run(self):
        self.db = sql.connect('file.db')
        try:
            while True:
                message = conn.recv(4096).decode()
                if SEP not in message:
                    conn.sendall(f'il messaggio deve contenere il carattere separatore {SEP}'.encode())
                    continue

                _m = message.split(';')

                req, val = _m[0], _m[1:]
                cur = self.db.cursor()
                if req == MESSAGE_REQUEST_NAME_FILE:
                    val = SEP.join(val)
                    res = cur.execute(f"SELECT * FROM files WHERE nome='{val}'").fetchall()
                    if len(res) == 1:
                        conn.sendall(f'il file {val} esiste'.encode())
                    else:
                        conn.sendall(f'il file {val} non esiste'.encode())
                elif req == MESSAGE_REQUEST_N_FRAMM:
                    val = SEP.join(val)
                    res = cur.execute(f"SELECT tot_frammenti FROM files WHERE nome='{val}'").fetchall()
                    if len(res) == 1:
                        conn.sendall(f'numero di frammenti del file {val}: {res[0][0]}'.encode())
                    else:
                        conn.sendall(f'il file {val} non esiste'.encode())
                elif req == MESSAGE_REQUEST_IP:
                    if len(val) != 2:
                        conn.sendall('il numero di parametri passati non è corretto'.encode())
                    else:
                        res = cur.execute(f"SELECT fr.host FROM files fi INNER JOIN frammenti fr ON fr.id_file = fi.id_file WHERE fi.nome = '{val[0]}' AND fr.n_frammento = {val[1]}").fetchall()
                        if len(res) == 1:
                            conn.sendall(f"ip dell'host del frammento {val[1]} del file {val[0]}: {res[0][0]}".encode())
                        else:
                            conn.sendall(f'impossibile avere un risultato'.encode())
                elif req == MESSAGE_REQUEST_EACH_IP:
                    val = SEP.join(val)
                    res = cur.execute(f"SELECT fr.host FROM files fi INNER JOIN frammenti fr ON fr.id_file = fi.id_file WHERE fi.nome = '{val}'").fetchall()
                    if len(res) == 0:
                        conn.sendall(f'il file {val} non esiste'.encode())
                    ips = [el[0] for el in res]
                    stringa = '\n'.join([f'frammento {i + 1}: {el}' for i, el in enumerate(ips)])
                    conn.sendall(stringa.encode())
                else:
                    conn.sendall('il comando richiesto non esiste'.encode())

                cur.close()
        except:
            conn.close()

server = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
server.bind(('0.0.0.0', 8000))
#db = sql.connect('file.db')
#cur = db.cursor()

while True:
    server.listen()
    conn, addr = server.accept()
    cl = Client(conn)
    cl.start()