import socket
import os

PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
CHUNKSIZE = 4096
SEPARATOR = "<SEPARATOR>"

def send_file_to_server(filename):
    """
    Mengirim file ke server.

    Args:
        filename (str): Nama file yang akan dikirim.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect(ADDR)
        client.send(b"SEND")
        if client.recv(1024).decode().strip() == "OK":
            client.send(filename.encode())
            send_file(client, filename)

def receive_file_from_server(filename):
    """
    Menerima file dari server.

    Args:
        filename (str): Nama file yang ingin diminta dari server.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect(ADDR)
        client.send(b"RECEIVE")
        if client.recv(1024).decode().strip() == "OK":
            client.send(filename.encode())
            response = client.recv(1024).decode()
            if response.startswith("ERROR"):
                print(response)
            else:
                filename, filesize = response.split(SEPARATOR)
                filename = os.path.basename(filename)
                filesize = int(filesize)
                with open(filename, "wb") as f:
                    received = 0
                    while received < filesize:
                        chunk = client.recv(CHUNKSIZE)
                        if not chunk: break
                        f.write(chunk)
                        received += len(chunk)
                print(f"File '{filename}' berhasil diterima.")

def send_file(conn, filename):
    """
    Mengirim file ke koneksi socket tertentu.

    Args:
        conn (socket.socket): Koneksi socket aktif.
        filename (str): Nama file yang akan dikirim.
    """
    filesize = os.path.getsize(filename)
    conn.send(f"{filename}{SEPARATOR}{filesize}".encode())
    with open(filename, "rb") as f:
        while chunk := f.read(CHUNKSIZE):
            conn.sendall(chunk)

if __name__ == "__main__":
    """
    Entry point dari program client. Menanyakan mode kirim/terima dan nama file.
    """
    mode = input("Ketik 1 untuk kirim, 2 untuk terima: ").strip()
    filename = input("Masukkan nama file: ").strip()
    if mode == "1":
        if os.path.exists(filename):
            send_file_to_server(filename)
        else:
            print("File tidak ditemukan.")
    elif mode == "2":
        receive_file_from_server(filename)
    else:
        print("Mode tidak valid.")
