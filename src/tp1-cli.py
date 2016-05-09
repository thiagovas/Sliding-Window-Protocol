# client.py

import pjd                   # Importa seu módulo
filename = 'recebido.txt'

s = pjd.activeOpen()        # Abre uma conexão

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
