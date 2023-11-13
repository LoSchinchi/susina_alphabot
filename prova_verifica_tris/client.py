import socket as sck

DISTANCE_CAMPI = 5
MESSAGE_YOUR_TURN = '__your_turn__'
TIME_TO_MOVE = '__time_to_move__'
MESSAGE_END_GAME = '__end_game__'


def printCampo(campo):
    righe = []
    for n in range(3):
        c = campo[n * 3: n * 3 + 3]
        line = '|'.join([f' {v} ' for v in c])
        indexes = '|'.join(f' {i + 3 * n} ' for i in range(len(c)))
        righe.append(line + (' ' * DISTANCE_CAMPI) + indexes)

    print(('\n---+---+---' + (' ' * DISTANCE_CAMPI) + '--+---+---\n').join(righe))
    print()


cl = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
cl.connect(('localhost', 8000))

print(cl.recv(4096).decode())
try:
    while True:
        mess = cl.recv(4096).decode()

        if MESSAGE_YOUR_TURN in mess:
            mess = mess[len(MESSAGE_YOUR_TURN):].split('--')
            printCampo(mess)

            mossa = None
            while True:
                mossa = int(input('inserisci il numero in base alla casella: '))
                if mossa >= len(mess) or mess[mossa] != ' ':
                    print('mossa impossibile da eseguire, ', end='')
                else:
                    print('attendi la mossa dell\'avversario\n')
                    break
            cl.sendall(f'{TIME_TO_MOVE}{mossa}'.encode())
        elif MESSAGE_END_GAME in mess:
            print(mess[len(MESSAGE_END_GAME):])
            cl.sendall(''.encode())
            cl.close()
except:
    cl.close()
