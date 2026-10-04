import random
import socket
import threading

class Server:
	def __init__(self, HOST, TCP_PORT, UDP_PORT):
		self.tcp_connections = []
		self.connections = []
		self.HOST = HOST
		self.TCP_PORT = TCP_PORT
		self.UDP_PORT = UDP_PORT

		self.sockTCP = None
		self.sockUDP = None

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
			port_udp_client = int(data.decode('utf-8'))
			self.connections.append((address[0], port_udp_client))
			self.tcp_connections.append(connection)
			print(f"Jogador conectado. IP: {address[0]} PORTA UDP: {port_udp_client}")


	#sortear palavra a ser desenhada/adivinhada
	def defineRandomWord(self):
		words = ["banana", "garrafa", "celular", "tesoura" ]
		randomWord = random.choice(words)
		return randomWord
	
	def roundServer(self, word, root):
		self.flagInverterPapeis = False
		print(f"Sua palavra sorteada é: {word}")
		#root = tk.Tk()
		#serverDraw(root, self.sockUDP)

		#gemini para matar a janela
		def check_end():
			if self.flagInverterPapeis:
				root.destroy()
			else:
				root.after(100, check_end)
		check_end()

		t_resp = threading.Thread(target=self.tryResponse, args=(word,), daemon=True) 
		t_resp.start()
		root.mainloop()
		t_resp.join()

	#verificar se a resposta está correta
	def tryResponse(self, word):
		#definir timer para o adversario tentar acertar a palavra
		self.sockUDP.settimeout(30) 
		client_addr = None
		#roda ate ele acertar ou o tempo acabar
		while not self.flagInverterPapeis:
			try:
				#aguarda mensagem do cliente
				data, addr = self.sockUDP.recvfrom(4096)
				client_addr = addr
				msg = data.decode('utf-8').strip()				

				if(msg.startswith("CHAT:")):
					word_recieve = msg.replace("CHAT:", "").strip()
					print(f"Resposta recebida de {addr}: {msg}")
					#inicia comparaçao de mensagem com resposta verdadeira

					if word_recieve.lower() == word.lower():  
						self.sockUDP.sendto("SYS:success".encode('utf-8'), addr)
						print(f"Acertou: {msg}")
						self.flagInverterPapeis = True
						break

					else:
						self.sockUDP.sendto("SYS:fail".encode('utf-8'), addr)
						print(f"Errado: '{msg}'")
				else:
					continue

			except socket.timeout:
				print("Tempo esgotado, ningúem acertou em 30 segundos!")
				if client_addr:
					try:
						self.sockUDP.sendto('SYS:timeout'.encode('utf-8'), client_addr)
					except:
						pass

				self.flagInverterPapeis = True		
			
			except Exception as e:
				print(f"Erro ao receber resposta: {e}")
				continue