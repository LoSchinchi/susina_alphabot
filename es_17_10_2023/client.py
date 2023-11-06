from socket import socket, AF_INET, SOCK_STREAM

client = socket(AF_INET, SOCK_STREAM)
client.connect(('192.168.1.118', 8800))

while True:
    client.sendall(input('inserisci un comando: ').encode())
    print(client.recv(4096).decode())
