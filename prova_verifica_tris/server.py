import socket as sck
from threading import Thread

MESSAGE_TURN = '__your_turn__'
TIME_TO_MOVE = '__time_to_move__'
STR_DRAW = '__draw__'
MESSAGE_END_GAME = '__end_game__'
table = [' ', 'x', ' ', 'o', 'o', 'o', ' ', ' ', 'x']

gioc1, gioc2 = None, None
turnOf, winner = None, None


class Client(Thread):
    def __init__(self, conn: sck.socket, symbol):
        Thread.__init__(self)
        self.conn = conn
        self.symbol = symbol

    def closeGame(self):
        global winner, gioc2, gioc1

        if winner == STR_DRAW:
            self.conn.sendall(f'{MESSAGE_END_GAME}la partita è terminata in parità'.encode())
        elif winner == self:
            self.conn.sendall(f'{MESSAGE_END_GAME}COMPLIMENTI, HAI VINTO!!'.encode())
        else:
            self.conn.sendall(f'{MESSAGE_END_GAME}sorry, hai perso'.encode())
        self.conn.close()
        if self == gioc1:
            gioc1 = None
        else:
            gioc2 = None


    def run(self):
        global gioc1, turnOf, gioc2, winner

        try:
            self.conn.sendall(f'il tuo simbolo è: {self.symbol}\nINIZIO PARTITA!!!'.encode())
            while True:
                if winner is not None:
                    break
                elif self == turnOf:
                    self.conn.sendall(f"{MESSAGE_TURN}{'--'.join(table)}".encode())

                    data = self.conn.recv(4096).decode()
                    if TIME_TO_MOVE in data:
                        ind = int(data[len(TIME_TO_MOVE):])
                        table[ind] = self.symbol

                        winner = getWinner()
                        if winner is None:
                            turnOf = gioc2 if self == gioc1 else gioc1
                        else:
                            turnOf = None

            # conn.close()
        except:
            conn.close()
            if self == gioc1:
                gioc1 = None
            else:
                gioc2 = None


def getWinner():
    global table

    for n in range(3):
        if table[n * 3] == table[n * 3 + 1] and table[n * 3] == table[n * 3 + 2] and table[n * 3] != ' ':
            return gioc1 if gioc1.symbol == table[n * 3] else gioc2
        elif table[n] == table[n + 3] and table[n] == table[n + 6] and table[n] != ' ':
            return gioc1 if gioc1.symbol == table[n] else gioc2

    if table[0] == table[4] and table[0] == table[8] and table[0] != ' ':
        return gioc1 if gioc1.symbol == table[0] else gioc2
    elif table[2] == table[4] and table[2] == table[6] and table[2] != ' ':
        return gioc1 if gioc1.symbol == table[2] else gioc2

    return STR_DRAW if table.count(' ') == 0 else None


server = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
server.bind(('0.0.0.0', 8000))

try:
    while True:
        if gioc1 is None or gioc2 is None:
            winner = None
            server.listen()
            conn, addr = server.accept()
            if gioc1 is None:
                gioc1 = Client(conn, 'x')
            else:
                gioc2 = Client(conn, 'o')
        elif winner is not None:
            gioc1.closeGame()
            gioc2.closeGame()
        elif turnOf is None:
            turnOf = gioc1
            gioc1.start()
            gioc2.start()

except:
    server.close()
