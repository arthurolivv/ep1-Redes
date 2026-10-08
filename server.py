import random
import socket
import threading
from roles import Drawer, Guesser

class Server(Drawer, Guesser):
	def __init__(self, HOST, TCP_PORT, UDP_PORT):
		self.tcp_connections = []
		self.connections = []
		self.HOST = HOST
		self.TCP_PORT = TCP_PORT
		self.UDP_PORT = UDP_PORT

		self.sockTCP = None
		self.sockUDP = None
		self.flagDesenhista = None
		self.flagInverterPapeis = None

	def start(self):
		
		try:
			#cria socket TCP pro handshake
			self.sockTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.sockTCP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.sockTCP.bind((self.HOST, self.TCP_PORT))
			print(f"Servidor TCP iniciado em {self.HOST}:{self.TCP_PORT}")
			threading.Thread(target=self.listen, args=(), daemon=True).start()
			#self.listen()

			#cria socket UDP para envio e recebimento de dados
			self.sockUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self.sockUDP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.sockUDP.bind((self.HOST, self.UDP_PORT))
			print(f"Servidor UDP iniciado em {self.HOST}:{self.UDP_PORT}")

		except socket.error as e:
			print(f"Erro ao criar sockets: {e}")
			return


	#abrir escuta de conexoes TCP
	def listen(self):
		self.sockTCP.listen()
		while True:
			#https://blog.devgenius.io/implementing-peer-to-peer-data-exchange-in-python-8e69513489af
			connection, address = self.sockTCP.accept()
			data = connection.recv(1024)
			msg = data.decode('utf-8')
			partes = msg.split(',')
			port_udp_client = int(partes[0].split(':')[1].strip()) ##MSG:porta
			self.flagDesenhista = bool(int(partes[1].strip()))#, flagtrueoufalse strip pra tirar o espaço antes

			self.connections.append((address[0], port_udp_client))
			self.tcp_connections.append(connection)
			print(f"Jogador conectado. IP: {address[0]} PORTA UDP: {port_udp_client}")