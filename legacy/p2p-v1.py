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