import tkinter as tk
import threading
from server import Server

color = ['black', 'red'] # black (#000000) e o red (#FF0000)

class gameInterface:
    def __init__(self, root, type, isDrawer, UDP_PORT=None):
        self.root = root
        self.type = type
        self.isDrawer = isDrawer
        self.sock = type.sockUDP
        self.UDP_PORT = type.UDP_PORT
        self.connections = []

        if isinstance(self.type, Server): 
            self.connections = type.connections
        else:
            #cliente envia desenhos pro servidor na porta definida, que 
            #repassa pro outro cliente dps
            self.connections = [(type.HOST, type.UDP_PORT)]
        
        if isDrawer:
            role = 'Desenhista'
        else:
            role = 'Adivinhador'

        self.root.title(f"Seu IP: {self.type.HOST} = {role}")
        self.root.attributes('-topmost', True)

        self.canvas = tk.Canvas(root, width=800, height=600, bg='white')
        self.canvas.pack()
        self.last_x, self.last_y = None, None
        
        if isDrawer:
            self.canvas.bind('<ButtonPress-1>', self.start_draw)
            self.canvas.bind('<B1-Motion>', self.draw)
            self.canvas.bind('<ButtonRelease-1>', self.stop_draw)
    
    def start_draw(self, event):
        self.last_x, self.last_y = event.x, event.y

    def draw(self, event):
        x, y = event.x, event.y
        self.draw_line(self.last_x, self.last_y, x, y, color[0])
        self.send_line(self.last_x, self.last_y, x, y, color[0])
        self.last_x, self.last_y = x, y

    def stop_draw(self, event):
        self.last_x, self.last_y = None, None
    
    # o fill aceita rgb. Teríamos o black (#000000) e o red (#FF0000)
    def draw_line(self, x1, y1, x2, y2, color):
        self.canvas.create_line(x1, y1, x2, y2, width=3, fill=color, capstyle=tk.ROUND, smooth=True)    
                
    def send_line(self, x1, y1, x2, y2, color):
        msg = f"DRAW:{x1},{y1},{x2},{y2},{color}\n"
        if self.connections:
            for conn in self.connections:
                self.sock.sendto(msg.encode('utf-8'), conn)
    
    def process_draw(self, msg):
            # Quebra a mensagem inteira separando pelos '\n'
            linhas = msg.split('\n')
            
            for line in linhas:
                if line and line.startswith("DRAW:"):
                    line = line.replace("DRAW:", "")
                    parts = line.split(',')

                    if len(parts) == 5:
                        x1, y1, x2, y2 = map(int, parts[:4])
                        line_color = parts[4]
                        self.root.after(0, self.draw_line, x1, y1, x2, y2, line_color)