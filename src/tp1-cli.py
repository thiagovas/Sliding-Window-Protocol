# coding: utf-8
# client.py

import pjd                   # Importa seu módulo
filename = 'recebido.txt'
PORT=55555                 # Porto onde o servidor vai esperar por conexões
SRV="10.0.0.2"      # Nome da máquina onde o servidor será executado


s = pjd.activeOpen(SRV,PORT) # Abre uma conexão

with open(filename, 'wb') as f:
    print 'Arquivo aberto/criado'
    while True:
        print('Recebendo dados...')
        data = s.recv(1024)        # Esse recv deve ser implementado por você
        if not data:
            break
        f.write(data)              # salva os dados no arquivo

f.close()
print('Arquivo recebido')
s.close()                          # Esse close deve ser implementado por você
print('Conexão fechada')
