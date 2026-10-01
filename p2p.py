import socket
import threading
import sys
import tkinter as tk
import random
import time

color = ['black', 'red'] # black (#000000) e o red (#FF0000)
pause = 1
palavra = 'teste'
connections = []
udp_address =[]
flagInverterPapeis = False
HOST = sys.argv[1] if len(sys.argv) > 1 else '0.0.0.0' #conecta no local host caso nao tenha o argumento do ip
PORT = 5555
UDP_PORT_DRAW = 6666
TCP_PORT_ANSWER = 6667



class serverDraw:
	def __init__(self, root, sock):
		self.sock = sock
		self.root = root
		self.root.title("Gartic Socket - Quadro Colaborativo")

		self.canvas = tk.Canvas(root, width=800, height=600, bg='white')
		self.root.attributes('-topmost', True)
		self.canvas.pack()

		self.last_x, self.last_y = None, None
		self.canvas.bind('<ButtonPress-1>', self.start_draw)
		self.canvas.bind('<B1-Motion>', self.draw)
		self.canvas.bind('<ButtonRelease-1>', self.stop_draw)

	def start_draw(self, event):
		self.last_x, self.last_y = event.x, event.y

	def draw(self, event):
		x, y = event.x, event.y
		self.draw_line(self.last_x, self.last_y, x, y, color[0])
		self.send_line(self.last_x, self.last_y, x, y, color[0])
		#self.send_line(self.sock,linha)
		self.last_x, self.last_y = x, y

	def stop_draw(self, event):
		self.last_x, self.last_y = None, None
    
    # o fill aceita rgb. Teríamos o black (#000000) e o red (#FF0000)
	def draw_line(self, x1, y1, x2, y2, color):
		self.canvas.create_line(x1, y1, x2, y2, width=3, fill=color, capstyle=tk.ROUND, smooth=True)
		
				
	def send_line(self, x1, y1, x2, y2, color):
		msg = f"{x1},{y1},{x2},{y2},{color}\n"
		if connections:
			self.sock.sendto(msg.encode('utf-8'), (connections[0],UDP_PORT_DRAW))


class clientDraw:
	def __init__(self, root, sock):
		self.sock = sock
		self.root = root
		self.root.title("Gartic Socket - Quadro Colaborativo")

		self.canvas = tk.Canvas(root, width=800, height=600, bg='white')
		self.root.attributes('-topmost', True)
		self.canvas.pack()
		self.color = color[0]
		self.last_x, self.last_y = None, None

		threading.Thread(target=self.receive_loop, daemon=True).start()

	def start_draw(self, event):
		self.last_x, self.last_y = event.x, event.y

	def draw(self, event):
		x, y = event.x, event.y
		self.draw_line(self.last_x, self.last_y, x, y, self.color)
		self.last_x, self.last_y = x, y

	def stop_draw(self, event):
		self.last_x, self.last_y = None, None
		
	# o fill aceita rgb. Teríamos o black (#000000) e o red (#FF0000)
	def draw_line(self, x1, y1, x2, y2, color):
		self.canvas.create_line(x1, y1, x2, y2, width=3, fill=color, capstyle=tk.ROUND, smooth=True)
	    
	def receive_loop(self):
		buffer = ""
		while True:
			try:
				data, addr = self.sock.recvfrom(4096)
				data = data.decode('utf-8')
				if not data:
					break
				buffer += data
				while '\n' in buffer:
					# Map vinha como int e str, gemini fez a boa #
					line, buffer = buffer.split('\n', 1)
					if line:
						parts = line.split(',')
						if len(parts) == 5:
							x1, y1, x2, y2 = map(int, parts[:4])
							line_color = parts[4]
							
							self.root.after(0, self.draw_line, x1, y1, x2, y2, line_color)
					#self.draw_line(x1, y1, x2, y2, self.color)
					# Map vinha como int e str, gemini fez a boa #
			except Exception:
				break






#funcao para conexao 
def listen():#escuta o handshake
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server.bind((HOST, PORT))
	server.listen()
	#https://blog.devgenius.io/implementing-peer-to-peer-data-exchange-in-python-8e69513489af
	connection, address = server.accept()
	connections.append(address[0])
	print(f"Accepted connection from {address}")
	connection.close() 
	server.close()



def connect():#conecta o handshake
	try:
		client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		client.connect((HOST,PORT))
		connections.append(client.getpeername()[0])
		client.close()
	except socket.error as e: 
		print(f"Erro na tentativa de conexão em {HOST}:{PORT}\n Erro: {e}")

def testarResposta(palavra):####servidor tcp
	global flagInverterPapeis
	serverResposta = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	serverResposta.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	serverResposta.bind(('0.0.0.0', TCP_PORT_ANSWER))
	serverResposta.listen(1)

	conn, addr = serverResposta.accept() # Aceita a conexao TCP do cliente


	
	while not flagInverterPapeis:
		data = conn.recv(4096) #4096 tamanho do buffer
		mensagem = data.decode('utf-8')
		print("Jogador: " + mensagem)
		if(mensagem.lower() == palavra.lower()):
			conn.sendall('certo'.encode('utf-8'))#usa conn já que o serverresposta é o de ouvir	
			print("Acertou\n")
			flagInverterPapeis = True
		else:
			conn.sendall('errado'.encode('utf-8'))
			print("errado\n")
		
	serverResposta.close()
		


def perguntarResposta():####cliente
	global flagInverterPapeis
	clienteResposta = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	conectado = False
	for i in range(10):
		try:
			clienteResposta.connect((connections[0], TCP_PORT_ANSWER))
			conectado = True
			break
		except ConnectionRefusedError:
			time.sleep(0.5)
	
	while not flagInverterPapeis:
		resposta = input("Palavra? ").strip()
		clienteResposta.sendall(resposta.encode('utf-8'))
		dados = clienteResposta.recv(4096)
		mensagem = dados.decode('utf-8')
		if mensagem == 'certo':
			flagInverterPapeis = True
			print("Você acertou!")
		else:
			print("Errado, tente novamente\n")
		

		

def sorteadorPalavras(): #sortear palavra a ser desennhada/adivinhada
      listaPalavras = ["banana", "garrafa", "celular", "tesoura" ]

      palavraSorteada = random.choice(listaPalavras)
      print(palavraSorteada)
      return palavraSorteada


##################################################################
##Região que estava no loop principal e o gemini mandou separar###
##################################################################
def rodada_servidor(palavra):
	serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	serverSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	root = tk.Tk()
	serverDraw(root, serverSock)

	#gemini para matar a janela
	def verificar_fim():
		if flagInverterPapeis:
			root.destroy()  # Fecha a janela do Tkinter para a rodada terminar!
		else:
			root.after(200, verificar_fim)  # Checa a cada 200m		
	verificar_fim()  # Inicia a checagem

	t_resp = threading.Thread(target=testarResposta, args=(palavra,), daemon=True) 
	
	t_resp.start()
	root.mainloop()
	t_resp.join()
	
def rodada_cliente():
	clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	clientSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	clientSock.bind((connections[0],UDP_PORT_DRAW))
	root = tk.Tk()
	clientDraw(root, clientSock)
	
	def verificar_fim():
		if flagInverterPapeis:
			root.destroy()  # Fecha a janela para encerrar a rodada!
		else:
			root.after(200, verificar_fim)

	verificar_fim()




	t_resp = threading.Thread(target=perguntarResposta, daemon=True)
	
		
	t_resp.start()
	root.mainloop()	
	t_resp.join()


def main():
	global flagInverterPapeis
	opcao = str(input("Hospedar um servidor ou Entrar em um servidor? (Responda com HOST ou JOIN)"))
	if opcao.lower() == "host":
		opcao1 = 0
	if opcao.lower() == "join":
		opcao1 = 1
	if(opcao1 == 0): #esta criando um servidor novo (servidor). Tem a prioridade para começar a desenhar na tela
		flagDesenhista = True
		palavra = sorteadorPalavras()
		threading.Thread(target=listen, daemon=True).start()
		while not connections:
			pass
	if(opcao1 == 1): #esta entrando em um servidor (cliente)
		flagDesenhista = False
		connect()
	while(pause):
		if(flagDesenhista):
			rodada_servidor(palavra)
            
		elif(not flagDesenhista):
			rodada_cliente()
		if (flagInverterPapeis):
			flagDesenhista = not flagDesenhista
			if flagDesenhista:
				palavra = sorteadorPalavras()
			flagInverterPapeis = False

if __name__ == '__main__':
    main()