import sys
import tkinter as tk
import threading
import os
from server import Server

color = ['black', 'red'] # black (#000000) e o red (#FF0000)

class gameInterface:
    def __init__(self, root, net_object, isDrawer, UDP_PORT=None):
        self.root = root
        self.net_object = net_object
        self.isDrawer = isDrawer
        self.cor = 0

        #apaga conteudo do canvas atual antes de iniciar um novo
        for widget in self.root.winfo_children():
            widget.destroy()

        self.sock = net_object.sockUDP
        self.UDP_PORT = net_object.UDP_PORT
        self.connections = []

        if isinstance(self.net_object, Server): 
            self.connections = net_object.connections
        else:
            #cliente envia desenhos pro servidor na porta definida, que 
            #repassa pro outro cliente dps
            self.connections = [(net_object.HOST, net_object.UDP_PORT)]
        
        if isDrawer:
            role = 'Desenhista'
        else:
            role = 'Adivinhador'

        self.root.title(f"Seu IP: {self.net_object.HOST} = {role}")
        self.root.attributes('-topmost', True)
        self.root.protocol("WM_DELETE_WINDOW", self.close_the_fucking_all)
        self.canvas = tk.Canvas(root, width=800, height=600, bg='white')
        self.canvas.pack()
        self.last_x, self.last_y = None, None
        
        if isDrawer:
            self.canvas.bind('<ButtonPress-1>', self.start_draw)
            self.canvas.bind('<B1-Motion>', self.draw)
            self.canvas.bind('<ButtonPress-2>', self.changeColor)
            self.canvas.bind('<ButtonPress-3>', self.changeColor)
            self.canvas.bind('<ButtonRelease-1>', self.stop_draw)
    
    def start_draw(self, event):
        self.last_x, self.last_y = event.x, event.y
    def changeColor(self, event):
        self.cor = 1 - self.cor #altera de 0 pra 1 ou 1 pra 0 de forma facil
            

    def draw(self, event):
        x, y = event.x, event.y
        self.draw_line(self.last_x, self.last_y, x, y, color[self.cor])
        self.send_line(self.last_x, self.last_y, x, y, color[self.cor])
        self.last_x, self.last_y = x, y

    def stop_draw(self, event):
        self.last_x, self.last_y = None, None
    
    # o fill aceita rgb. Teríamos o black (#000000) e o red (#FF0000)
    def draw_line(self, x1, y1, x2, y2, color):
        self.canvas.create_line(x1, y1, x2, y2, width=3, fill=color, capstyle=tk.ROUND, smooth=True)    
                
    def send_line(self, x1, y1, x2, y2, color):
        msg = f"DRAW:{x1},{y1},{x2},{y2},{color}\n" ####COR e vetor
        if self.connections:
            for conn in self.connections:
                self.sock.sendto(msg.encode('utf-8'), conn)
    
    def process_draw(self, msg):
            # Quebra a mensagem inteira separando pelos '\n'
            lines = msg.split('\n')
            
            for line in lines:
                #processar desenho
                if line and line.startswith("DRAW:"):
                    line = line.replace("DRAW:", "")
                    parts = line.split(',')

                    if len(parts) == 5:
                        x1, y1, x2, y2 = map(int, parts[:4])
                        line_color = parts[4]
                        self.root.after(0, self.draw_line, x1, y1, x2, y2, line_color)


    def close_the_fucking_all(self):
        print("Janela Fechada, avisando o outro jogador...")
        msg = f"CLOSE: closeEverything\n" #a parte q realmente importa aqui é o CLOSE:
        if self.connections:
                for conn in self.connections:
                    try:
                        #envia no minimo 20x para garantir a entrega e nenhum pacoter se perder
                        for i in range(20):
                            self.sock.sendto(msg.encode('utf-8'), conn)
                    except Exception:
                        pass
        self.root.destroy()
        os._exit(0)

                      
