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
flagDesenhista = None
client = None
server = None
flagInverterPapeis = False

def main():
    global flagDesenhista
    global flagInverterPapeis
    net_object = None
    
    try:
        opcao = int(input("Hospedar (0) ou Entrar (1) em um servidor?"))
        if(opcao == 0): #esta criando um servidor novo (servidor). Tem a prioridade para começar a desenhar na tela
            flagDesenhista = True
            net_object = Server(HOST, TCP_PORT, UDP_PORT)
            net_object.start()
            while len(net_object.connections) == 0: # Sugestão do claude para não consumir CPU enquanto aguarda conexões
                time.sleep(0.1) 
                
        elif(opcao == 1): #esta entrando em um servidor (cliente)
            flagDesenhista = False
            net_object = Client()
            net_object.connectTo(HOST, TCP_PORT, UDP_PORT) 
        
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