import sys
import time
import random
import threading
import socket
import tkinter as tk
from time import sleep
 
from interface import gameInterface
from server import Server
from client import Client
 
BIND_ADDRESS = '0.0.0.0'  # host escuta em TODAS as interfaces (aceita conexões de outros PCs da rede)
TCP_PORT = 5555
UDP_PORT = 5556
 
pause = True
flagDesenhista = None
client = None
server = None
flagInverterPapeis = False
 
 
def getLocalIp():
    # descobre o IP desta máquina na rede local (é o que o outro computador precisa digitar)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))  # UDP: não envia nada, só descobre qual interface seria usada
        return s.getsockname()[0]
    except OSError:
        return '127.0.0.1'
    finally:
        s.close()

def askHostIp():
    # o IP do host pode vir por argumento (python main.py 192.168.0.10) ou ser digitado
    if len(sys.argv) > 1:
        return sys.argv[1]
    ip = input("IP do computador que está hospedando (Enter para 127.0.0.1): ").strip()
    return ip or '127.0.0.1'

def main():
    global flagDesenhista
    global flagInverterPapeis
    net_object = None
    
    try:
        opcao = str(input("Hospedar um servidor ou Entrar em um servidor? (Responda com HOST ou JOIN)\n"))
        
        if opcao.lower() == "host":
            opcao1 = 0
        if opcao.lower() == "join":
            opcao1 = 1
        
        if(opcao1 == 0): #esta criando um servidor novo (servidor). Tem a prioridade para começar a desenhar na tela
            net_object = Server(BIND_ADDRESS, TCP_PORT, UDP_PORT)
            net_object.start()
            while len(net_object.connections) == 0: # Sugestão do claude para não consumir CPU enquanto aguarda conexões
                time.sleep(0.1) 
            flagDesenhista = net_object.flagDesenhista
                
        elif(opcao1 == 1): #esta entrando em um servidor (cliente)
            host_ip = askHostIp()
            net_object = Client()
            flagDesenhista = int(random.randint(0,1))
            net_object.connectTo(host_ip, TCP_PORT, UDP_PORT, flagDesenhista)
        
    except ValueError as e:
        print(f"Opção Inválida: {e} \n Encerrando o programa.")
        sys.exit(1)

    root = tk.Tk()
    while(pause):

        if(flagDesenhista):
            drawer_interface = gameInterface(root, net_object, isDrawer=True, UDP_PORT=UDP_PORT)
            word = net_object.defineRandomWord()
            net_object.roundDrawer(word, root)
            
        elif(not flagDesenhista):
            viewer_interface = gameInterface(root, net_object, isDrawer=False, UDP_PORT=UDP_PORT)
            net_object.roundGuesser(root, viewer_interface)

        if net_object.flagInverterPapeis:
            print("\nPapeis invertidos! O desenhista agora é o adivinhador e vice-versa.")
            net_object.flagInverterPapeis = False

        else:
            print("\nNinguém acertou! Trocando de papéis...")

        flagDesenhista = not flagDesenhista  
        sleep(1)

if __name__ == '__main__':
    main()