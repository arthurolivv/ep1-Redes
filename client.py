import socket
import threading
import tkinter as tk

class Client:
	def __init__(self):
		self.HOST = None
		self.TCP_PORT = None
		self.UDP_PORT = None
		self.sockTCP = None
		self.sockUDP = None

		self.flagInverterPapeis = False

	#inicia handshake TCP com o servidor
	def connectTo(self, HOST_TARGET, TCP_PORT_TARGET, UDP_PORT_TARGET):
		self.HOST = HOST_TARGET
		self.TCP_PORT = TCP_PORT_TARGET
		self.UDP_PORT = UDP_PORT_TARGET

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
			self.sockTCP.sendall(str(my_portUDP).encode('utf-8'))

		except socket.error as e: 
			print(f"Erro na tentativa de handshake em {self.HOST}:{self.TCP_PORT}\n Erro: {e}")
	
	def roundClient(self, root, interface):
		self.flagInverterPapeis = False

		#gemini para matar a janela
		def check_end():
			if self.flagInverterPapeis:
				root.destroy()
			else:
				root.after(100, check_end)
		check_end()

		t_listen = threading.Thread(target=self.listen_server, args=(interface,), daemon=True)
		t_listen.start()

		t_resp = threading.Thread(target=self.askResponse, daemon=True)
		t_resp.start()
		root.mainloop()	
		t_resp.join()

	def listen_server(self, interface):
		while not self.flagInverterPapeis:
			try:
				#recebe mensagem do servidor
				data, addr = self.sockUDP.recvfrom(4096)
				msg = data.decode('utf-8')

				if(msg.startswith("SYS:")):
					word_recieve = msg.replace("SYS:", "").strip()
					if word_recieve == "success":
						self.flagInverterPapeis = True
						print("Parabéns, você acertou!\n")

					elif word_recieve == "fail":
						self.flagInverterPapeis = False
						print("Errou, tente novamente.\n")

					elif word_recieve == "timeout":
						self.flagInverterPapeis = True
						print("Tempo esgotado!")

				elif msg.startswith("DRAW:"):
					interface.process_draw(msg)

			except Exception:
				break

	def askResponse(self):
		while not self.flagInverterPapeis:
			try:
				response = str(input("Insira sua tentativa de resposta:\n")).strip()
				
				#recomendaçao do claude para não enviar mensagens vazias e entupir o servidor
				if not response:
					print("Resposta vazia, tente novamente.")
					continue

				send = f"CHAT:{response}\n"
				self.sockUDP.sendto(send.encode('utf-8'), (self.HOST, self.UDP_PORT))

			except Exception as e:
				print(f"Erro ao enviar resposta: {e}")