import socket
import threading
import sys
import tkinter as tk
import random

color = ['black', 'red'] # black (#000000) e o red (#FF0000)
pause = 1
palavra = 'teste'
connections = []
udp_address =[]
flagInverterPapeis = False
HOST = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1' #conecta no local host caso nao tenha o argumento do ip
PORT = 5555
UDP_PORT = 6666


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
		self.sock.sendto(msg.encode('utf-8'), (connections[0],UDP_PORT))

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


def connect():#conecta o handshake
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST,PORT))
        connections.append(client.getpeername()[0])
    except socket.error as e: 
        print(f"Erro na tentativa de conexão em {HOST}:{PORT}\n Erro: {e}")

def testarResposta(palavra):####servidor
	global flagInverterPapeis
	serverResposta = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	serverResposta.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	serverResposta.bind((HOST, UDP_PORT))
    
	data, addr = serverResposta.recvfrom(4096) #4096 tamanho do buffer
	mensagem = data.decode('utf-8')
	if(mensagem == palavra):
		serverResposta.sendto('certo'.encode('utf-8'), addr)
		print("Acertou\n")
		flagInverterPapeis = True
	else:
		serverResposta.sendto('errado'.encode('utf-8'), addr)
		print("errado\n")
	serverResposta.close()
		
def perguntarResposta():####cliente
	global flagInverterPapeis
	resposta = str(input("Palavra?\n")) 
	clienteResposta = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	clienteResposta.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	
	clienteResposta.sendto(resposta.encode('utf-8'), (connections[0],UDP_PORT))
	dados_resposta, addr = clienteResposta.recvfrom(4096)
	mensagem = dados_resposta.decode('utf-8')
	if(mensagem == 'certo'):
		flagInverterPapeis = True
		print("Acertou\n")
	else:
		print("errado\n")
	clienteResposta.close()
		

def sorteadorPalavras(): #sortear palavra a ser desennhada/adivinhada
      listaPalavras = ["banana", "garrafa", "celular", "tesoura" ]

      palavraSorteada = random.choice(listaPalavras)

      return palavraSorteada

def sendData(dados):
    for connection in connections:
        try:
            connection.sendall(dados.encode())
        except socket.error as e:
            print(f"Falha ao enviar dados. Erro: {e}")
            connections.remove(connection)



##################################################################
##Região que estava no loop principal e o gemini mandou separar###
##################################################################
def rodada_servidor(palavra):
	serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	serverSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	root = tk.Tk()
	serverDraw(root, serverSock)
	
	t_resp = threading.Thread(target=testarResposta, args=(palavra,), daemon=True) 
	
	t_resp.start()
	root.mainloop()
	t_resp.join()
	
def rodada_cliente():
	clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	clientSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	clientSock.bind(('0.0.0.0',UDP_PORT))
	root = tk.Tk()
	clientDraw(root, clientSock)
	
	t_resp = threading.Thread(target=perguntarResposta, daemon=True)
	
		
	t_resp.start()
	root.mainloop()	
	t_resp.join()


def main():
	global flagInverterPapeis
	opcao = int(input("Hospedar um servidor ou Entrar em um servidor? (Responda com 0 ou 1)"))
	if(opcao == 0): #esta criando um servidor novo (servidor). Tem a prioridade para começar a desenhar na tela
		flagDesenhista = True
		threading.Thread(target=listen, daemon=True).start()
		while not connections:
			pass
	if(opcao == 1): #esta entrando em um servidor (cliente)
		flagDesenhista = False
		connect()
	while(pause):
		if(flagDesenhista):
			palavra = sorteadorPalavras()
			rodada_servidor(palavra)
            
		elif(not flagDesenhista):
			rodada_cliente()
		if (flagInverterPapeis):
			flagDesenhista = not flagDesenhista
			flagInverterPapeis = False

if __name__ == '__main__':
    main()