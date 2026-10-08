import random
import select
import socket
import sys
import threading
import time


class Drawer:
    #sortear palavra a ser desenhada/adivinhada
    def defineRandomWord(self):
        words = ["banana", "garrafa", "celular", "tesoura" ]
        randomWord = random.choice(words)
        return randomWord

    def roundDrawer(self, word, root):
        self.flagInverterPapeis = False
        print(f"Sua palavra sorteada é: {word}")


        #dica do gemini: pausar a janela do Tkinter sem precisar destrui-la e nao ocupar a thread
        self._timer_id = None

        def check_end():
            if self.flagInverterPapeis:
                root.quit()
            else:
                self._timer_id = root.after(100, check_end)
        check_end()

        t_resp = threading.Thread(target=self.tryResponse, args=(word,), daemon=True) 
        t_resp.start()
        root.mainloop()

        if self._timer_id:
            root.after_cancel(self._timer_id)
        
        t_resp.join()

    #verificar se a resposta está correta
    def tryResponse(self, word):

        self.sockUDP.settimeout(1) 
        client_addr = None  
        start_time = time.time()

        #roda ate ele acertar ou o tempo acabar
        while not self.flagInverterPapeis:

            #verifica se o tempo de adivinhação foi excedido, se sim -> inverte os papeis
            if time.time() - start_time >= 30:
                if client_addr:
                    try:
                        self.sockUDP.sendto(b'SYS:timeout', client_addr)
                    except:
                        pass
                self.flagInverterPapeis = True
                break
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
                if time.time() - start_time >= 30:
                    print("\nTempo esgotado, ninguém acertou em 30 segundos!")
                    if client_addr:
                        try:
                            self.sockUDP.sendto('SYS:timeout'.encode('utf-8'), client_addr)
                        except:
                            pass
                    self.flagInverterPapeis = True
                    break
                continue	
            
            except Exception as e:
                print(f"Erro ao receber resposta: {e}")
                continue

class Guesser:

    def roundGuesser(self, root, interface):
        self.flagInverterPapeis = False
        self._timer_id = None

        #garantia para caso o pacote UDP de timeout for perdido o jogador n ficar preso
        deadline = time.time() + 33  # 30s de round + 3s extras pra atraso de pacotes


        #dica do gemini: pausar a janela do Tkinter sem precisar destrui-la
        def check_end():
            if self.flagInverterPapeis or time.time() >= deadline:
                root.quit()
            else:
                self._timer_id = root.after(100, check_end)
                check_end()

        t_listen = threading.Thread(target=self.listen_server, args=(interface,), daemon=True)
        t_listen.start()

        t_resp = threading.Thread(target=self.askResponse, daemon=True)
        t_resp.start()

        root.mainloop()	

        if self._timer_id:
            root.after_cancel(self._timer_id)

        t_listen.join()
        t_resp.join()

    def listen_server(self, interface):
        #timeout pra revfrom nao rodar infinitamente e travar thread
        self.sockUDP.settimeout(1.0)
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
                    #interface.process_draw(msg)
                    interface.root.after(0, interface.process_draw, msg)

            except socket.timeout:
                continue
            except Exception as e:
                print(f"Erro listen_server: {e}")
                continue

    # def askResponse(self):
    #     print("Insira sua tentativa de resposta:")
    #     while not self.flagInverterPapeis:
    #         try:
    #             #espera 1 segundo por um input no terminal se nada for digitado ignora e reinicia desse jeito nao trava a thread 
    #             ready_outputs, _, _ = select.select([sys.stdin], [], [], 1.0)
                    
    #             if ready_outputs:
    #                 response = sys.stdin.readline().strip()
                    
    #                 if not response:
    #                     continue

    #                 send = f"CHAT:{response}\n"
    #                 self.sockUDP.sendto(send.encode('utf-8'), (self.HOST, self.UDP_PORT))

    #         except Exception as e:
    #             print(f"Erro ao enviar resposta: {e}")

    def askResponse(self):
        print("Insira sua tentativa de resposta:")
        while not self.flagInverterPapeis:
            try:
                #espera 1 segundo por um input no terminal se nada for digitado ignora e reinicia desse jeito nao trava a thread 
                ready_outputs, _, _ = select.select([sys.stdin], [], [], 1.0)
                    
                if ready_outputs:
                    response = sys.stdin.readline().strip()

                    if response:
                        send = f"CHAT:{response}\n"
                    
                        #sugestao do gemini para verificar se o objeto instanciado que ira perguntar 
                        #se existe uma lista de conexoes -> se tiver: o objeto é um servidor
                        #e pega o IP e porta do cliente
                        if hasattr(self, 'connections') and len(self.connections) > 0:
                            dest = self.connections[0]
                        else:
                            dest = (self.HOST, self.UDP_PORT)
                            
                        self.sockUDP.sendto(send.encode('utf-8'), dest)

            except Exception as e:
                print(f"Erro ao enviar resposta: {e}")