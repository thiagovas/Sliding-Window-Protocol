# server.py

import pjd                 # Importa seu módulo 
filename='tp1.txt'         # Garanta que esse arquivo existe
PORT=55555                 # Porto onde o servidor vai esperar por conexões

print 'Servidor iniciando....'
conn, addr = pjd.passiveOpen(PORT) # Passive open inicia o lado do servidor
print 'Recebeu conexão originada em ', addr

f = open(filename,'rb')
l = f.read(1024)
while (l):
    conn.send(l)           # você deve implementar essa função
    l = f.read(1024)
f.close()

print('Fim do envio')
conn.close()               # você deve implementar essa função
