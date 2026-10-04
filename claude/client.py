import socket
import threading
import sys
import tkinter as tk

HOST = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1'
PORT = 5555


class DrawApp:
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

        threading.Thread(target=self.receive_loop, daemon=True).start()

    def start_draw(self, event):
        self.last_x, self.last_y = event.x, event.y

    def draw(self, event):
        x, y = event.x, event.y
        self.draw_line(self.last_x, self.last_y, x, y)
        self.send_line(self.last_x, self.last_y, x, y)
        self.last_x, self.last_y = x, y

    def stop_draw(self, event):
        self.last_x, self.last_y = None, None

    # o fill aceita rgb. Teríamos o black (#000000) e o red (#FF0000)
    def draw_line(self, x1, y1, x2, y2):
        self.canvas.create_line(x1, y1, x2, y2, width=3, fill='black',
                                 capstyle=tk.ROUND, smooth=True)

    def send_line(self, x1, y1, x2, y2):
        msg = f"{x1},{y1},{x2},{y2}\n"
        try:
            self.sock.sendall(msg.encode())
        except Exception:
            pass

    def receive_loop(self):
        buffer = ""
        while True:
            try:
                data = self.sock.recv(4096).decode()
                if not data:
                    break
                buffer += data
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line:
                        x1, y1, x2, y2 = map(int, line.split(','))
                        self.draw_line(x1, y1, x2, y2)
            except Exception:
                break


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # socket.SOCK_STREAM TCP # socket.SOCK_DGRAM UDP
    sock.connect((HOST, PORT))

    root = tk.Tk()
    DrawApp(root, sock)
    root.mainloop()


if __name__ == '__main__':
    main()
