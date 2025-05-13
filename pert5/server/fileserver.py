import socket
import threading
import os

PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
CHUNKSIZE = 4096
SEPARATOR = "<SEPARATOR>"

def start_server():
    """
    Memulai server untuk menerima koneksi dan memproses file yang dikirim/diterima dari client.
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f"[LISTENING] Server listening on {SERVER}:{PORT}")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()

def handle_client(conn, addr):
    """
    Menangani koneksi client berdasarkan perintah yang dikirim (SEND atau RECEIVE).

    Args:
        conn (socket.socket): Objek koneksi socket.
        addr (tuple): Alamat client.
    """
    print(f"[NEW CONNECTION] {addr}")
    try:
        cmd = conn.recv(1024).decode().strip()
        if cmd == "SEND":
            conn.send("OK".encode())
            filename = conn.recv(1024).decode().strip()
            receive_file(conn)
            print(f"[RECEIVED] File '{filename}' dari {addr}")

        elif cmd == "RECEIVE":
            conn.send("OK".encode())
            filename = conn.recv(1024).decode().strip()
            if os.path.exists(filename):
                send_file(conn, filename)
                print(f"[SENT] File '{filename}' ke {addr}")
            else:
                conn.send("ERROR: File not found".encode())
                conn.shutdown(socket.SHUT_WR)
                print(f"[ERROR] File '{filename}' tidak ditemukan")

        else:
            print(f"[INVALID CMD] {addr}: {cmd}")
    except Exception as e:
        print(f"[EXCEPTION] {addr}: {e}")
    finally:
        conn.close()
        print(f"[DISCONNECTED] {addr}")

def send_file(conn, filename):
    """
    Mengirim file ke client.

    Args:
        conn (socket.socket): Objek koneksi socket.
        filename (str): Nama file yang akan dikirim.
    """
    filesize = os.path.getsize(filename)
    conn.send(f"{filename}{SEPARATOR}{filesize}".encode())
    with open(filename, "rb") as f:
        while chunk := f.read(CHUNKSIZE):
            conn.sendall(chunk)

def receive_file(conn):
    """
    Menerima file dari client dan menyimpannya di server.

    Args:
        conn (socket.socket): Objek koneksi socket.
    """
    meta = conn.recv(1024).decode()
    filename, filesize = meta.split(SEPARATOR)
    filename = os.path.basename(filename)
    filesize = int(filesize)
    with open(filename, "wb") as f:
        received = 0
        while received < filesize:
            chunk = conn.recv(CHUNKSIZE)
            if not chunk: break
            f.write(chunk)
            received += len(chunk)

if __name__ == "__main__":
    """
    Entry point dari program server.
    """
    start_server()
