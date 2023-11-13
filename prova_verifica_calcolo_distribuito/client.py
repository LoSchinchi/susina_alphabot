import socket as sck

s = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
s.connect(('localhost', 5000))

print(s.recv(4096).decode())
while True:
    data = s.recv(4096).decode()
    if data == 'exit':
        s.close()
        break
    else:
        print(f'>> {data}')
        ris = eval(data)
        print(ris)
        s.sendall(f'{ris}'.encode())
