import socket
import threading
import tkinter as tk

class Client:
	def __init__(self):
		self.HOST_TARGET = None
		self.TCP_PORT_TARGET = None
		self.UDP_PORT_TARGET = None
		self.sockTCP = None
		self.sockUDP = None

		self.flagInverterPapeis = False

	#inicia handshake TCP com o servidor
	def connectTo(self, HOST_TARGET, TCP_PORT_TARGET, UDP_PORT_TARGET):
		self.HOST_TARGET = HOST_TARGET
		self.TCP_PORT_TARGET = TCP_PORT_TARGET
		self.UDP_PORT_TARGET = UDP_PORT_TARGET

		try:
			#cria socket TCP para handshake e conecta ao servidor
			self.sockTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.sockTCP.connect((self.HOST_TARGET, self.TCP_PORT_TARGET))

			#apenas cria socket UDP para envio e recebimento de dados
			self.sockUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self.sockUDP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.sockUDP.bind(('0.0.0.0', self.UDP_PORT_TARGET))

		except socket.error as e: 
			print(f"Erro na tentativa de conexão em {self.HOST_TARGET}:{self.TCP_PORT_TARGET}\n Erro: {e}")
	
	def roundClient(self, root):
		self.flagInverterPapeis = False

		#gemini para matar a janela
		def check_end():
			if self.flagInverterPapeis:
				root.destroy()
			else:
				root.after(100, check_end)
		check_end()

		t_resp = threading.Thread(target=self.askResponse, daemon=True)
		t_resp.start()
		root.mainloop()	
		t_resp.join()

	def askResponse(self):
		response = str(input("Insira sua tentativa de resposta:\n")).strip()

		if not response:
			print("Resposta vazia. Encerrando a tentativa.")
			return

		self.sockUDP.settimeout(15)
		
		try:
			while True:
				self.sockUDP.sendto(response.encode('utf-8'), (self.HOST_TARGET, self.UDP_PORT_TARGET))
				
				#recupera mensagem do servidor
				data_response, addr = self.sockUDP.recvfrom(4096)
				msg = data_response.decode('utf-8')

				if(msg == True):
					self.flagInverterPapeis = True
					print("Acertou\n")
					break
				else:
					self.flagInverterPapeis = False
					print("Errou\n")

		except socket.timeout:
			print("Tempo esgotado!")
			self.flagInverterPapeis = False

		except Exception as e:
			print(f"Erro ao receber resposta: {e}")
			self.flagInverterPapeis = False