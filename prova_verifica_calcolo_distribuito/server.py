import socket as sck
import sqlite3 as sql
from threading import Thread
from time import sleep


class Client(Thread):
    def __init__(self, id, conn: sck.socket, addr):
        Thread.__init__(self)
        self.id = id
        self.conn = conn
        self.addr = addr

    def run(self):
        global operations

        try:
            self.conn.sendall(f'id del client: {self.id}'.encode())
            for diz in operations:
                if diz['client'] == self.id:
                    self.conn.sendall(diz['operation'].encode())
                    print(f"{diz['operation']} = {self.conn.recv(4096).decode()} from {self.addr[0]} - {self.addr[1]}")

            self.conn.sendall('exit'.encode())
            self.conn.close()
        except:
            conn.close()


db = sql.connect('operations.db')
cur = db.cursor()
operations = []
for id, client, op in cur.execute('SELECT * FROM operations').fetchall():
    operations.append({'id': id, 'client': client, 'operation': op})
cur.close()
db.close()

server = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
server.bind(('0.0.0.0', 5000))

n_cl = 1
while True:
    server.listen()
    conn, addr = server.accept()
    cl = Client(n_cl, conn, addr)
    cl.start()
    n_cl += 1

server.close()
