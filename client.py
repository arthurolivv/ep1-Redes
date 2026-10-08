import select
import socket
import sys
import tkinter as tk

from roles import Drawer, Guesser

class Client(Drawer, Guesser):
	def __init__(self):
		self.HOST = None
		self.TCP_PORT = None
		self.UDP_PORT = None
		self.sockTCP = None
		self.sockUDP = None
		
		self.flagInverterPapeis = False

	#inicia handshake TCP com o servidor
	def connectTo(self, HOST_TARGET, TCP_PORT_TARGET, UDP_PORT_TARGET, flagDesenhista):
		self.HOST = HOST_TARGET
		self.TCP_PORT = TCP_PORT_TARGET
		self.UDP_PORT = UDP_PORT_TARGET
		self.flagDesenhista = flagDesenhista
		try:
			#cria socket TCP para handshake e conecta ao servidor
			self.sockTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.sockTCP.connect((self.HOST, self.TCP_PORT))
			#self.sockTCP.close()

			#apenas cria socket UDP para envio e recebimento de dados
			self.sockUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self.sockUDP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

			#self.sockUDP.bind(('0.0.0.0', self.UDP_PORT))
			
			#como os testes estao sendo feitos em uma mesma maquina, essa linha 
			#abaixo serve para criarmos um socket udp em alguma porta livre 
			#do cliente para nao conflitar com socket do servidor
			self.sockUDP.bind(('0.0.0.0', 0))
			my_portUDP = self.sockUDP.getsockname()[1]
			self.sockTCP.sendall(f"MSG:{str(my_portUDP)}, {int(not self.flagDesenhista)}\n".encode('utf-8'))

		except socket.error as e: 
			print(f"Erro na tentativa de handshake em {self.HOST}:{self.TCP_PORT}\n Erro: {e}")