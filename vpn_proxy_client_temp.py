import socket
import threading
from cryptography.fernet import Fernet

# encryption key — must match the one on the server
key = 'key here'
cipher = Fernet(key)

# Remote VPN server
SERVER_IP = 'ip'
SERVER_PORT = 5555

# Local proxy settings
LISTEN_IP = ""
LISTEN_PORT = 1080

def handle_client(client_socket):
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((SERVER_IP, SERVER_PORT))

    def forward(src, dst, encrypt=False, decrypt=False):
        while True:
            try:
                data = src.recv(4096)
                if not data:
                    break
                if encrypt:
                    data = cipher.encrypt(data)
                if decrypt:
                    data = cipher.decrypt(data)
                dst.sendall(data)
            except:
                break

    threading.Thread(target=forward, args=(client_socket, remote_socket, True)).start()
    threading.Thread(target=forward, args=(remote_socket, client_socket, False, True)).start()

def start_proxy():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((LISTEN_IP, LISTEN_PORT))
    server.listen(5)
    print(f"[+] Proxy listening on {LISTEN_IP}:{LISTEN_PORT}")

    while True:
        client_socket, addr = server.accept()
        threading.Thread(target=handle_client, args=(client_socket,)).start()

if __name__ == "__main__":
    start_proxy()
