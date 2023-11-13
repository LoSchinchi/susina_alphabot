import socket as sck

cl = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
cl.connect(('localhost', 8000))
while True:
    print('cosa vuoi sapere:')
    print('se un file esiste                       -> filename;<<nome_del_file>>')
    print('il numero di frammenti di un file       -> nframm;<<nome_del_file>>')
    print('ip del frammento n al file f            -> getip;<<nome_del_file>>;<<num_frammento>>')
    print('tutti gli ip di ogni frammento del file -> eachip;<<nome_del_file>>')
    val = input('>> ')
    cl.sendall(val.encode())
    print(cl.recv(4096).decode())
    print()