import socket
import threading

HOST = '0.0.0.0'
PORT = 5555

clients = []  # lista de sockets conectados
lock = threading.Lock()


def broadcast(data, sender_conn):
    """Reenvia os dados recebidos de um cliente para todos os outros."""
    with lock:
        for c in clients:
            if c is not sender_conn:
                try:
                    c.sendall(data)
                except Exception:
                    pass


def handle_client(conn, addr):
    print(f"[+] Conectado: {addr}")
    with lock:
        clients.append(conn)

    with conn:
        while True:
            try:
                data = conn.recv(4096)
                if not data:
                    break
                broadcast(data, conn)
            except ConnectionError:
                break

    with lock:
        clients.remove(conn)
    print(f"[-] Desconectado: {addr}")


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Servidor rodando em {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(server, addr), daemon=True).start()


if __name__ == '__main__':
    main()