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

HOST = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1' #conecta no local host caso nao tenha o argumento do ip
TCP_PORT = 5555
UDP_PORT = 5556

pause = True
flagDesenhista = False
client = None
server = None

def main():
    global flagDesenhista
    server, client = None, None
    
    try:
        opcao = int(input("Hospedar (0) ou Entrar (1) em um servidor?"))
        if(opcao == 0): #esta criando um servidor novo (servidor). Tem a prioridade para começar a desenhar na tela
            flagDesenhista = True
            server = Server(HOST, TCP_PORT, UDP_PORT)
            server.start()
            while len(server.connections) == 0: # Sugestão do claude para não consumir CPU enquanto aguarda conexões
                time.sleep(0.1) 
                
        elif(opcao == 1): #esta entrando em um servidor (cliente)
            flagDesenhista = False
            client = Client()
            client.connectTo(HOST, TCP_PORT, UDP_PORT) 
        
    except ValueError as e:
        print(f"Opção Inválida: {e} \n Encerrando o programa.")
        sys.exit(1)

    while(pause):
        if(flagDesenhista):
            root = tk.Tk()
            drawer_interface = gameInterface(root, server, isDrawer=True, UDP_PORT=UDP_PORT)
            word = server.defineRandomWord()
            server.roundServer(word, root)
            
        elif(not flagDesenhista):
            root = tk.Tk()
            viewer_interface = gameInterface(root, client, isDrawer=False, UDP_PORT=UDP_PORT)
            client.roundClient(root)
            time.sleep(15)

        check_response = False
        if server and server.flagInverterPapeis:
            flagDesenhista = not flagDesenhista
            check_response = True
            server.flagInverterPapeis = False

        if client and client.flagInverterPapeis:
            flagDesenhista = not flagDesenhista
            check_response = True
            client.flagInverterPapeis = False

        if check_response:
            print("Papeis invertidos! O desenhista agora é o adivinhador e vice-versa.")
            flagDesenhista = not flagDesenhista

if __name__ == '__main__':
    main()