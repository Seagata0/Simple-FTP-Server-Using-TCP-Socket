import socket
import time
import sys
import os
import struct

# Inisialisasi variabel-variabel untuk koneksi dan transfer data
IP = 'localhost'
PORT = 2023
BUFFER_SIZE = 1024

# Fungsi untuk menampilkan daftar file di server
def list_files(s):
    s.send(b'LIST') #mengirim request list
    files_str = s.recv(BUFFER_SIZE).decode()
    print("Files in Drive:")
    print(files_str)

# Fungsi untuk mengunggah file ke server
def upload_file(s, filename):
    file_size = os.path.getsize(filename)
    s.   filename dan size
    with open(filename, 'rb') as file: #open file dengan mode readbinary
        while True: #loop mengirim data ke server dengan ukuran 1024byte per pengiriman
            data = file.read(1024)
            if not data: #kalau data habis loop berhenti
                break
            s.send(data)
    print(f"File '{filename}' uploaded successfully.")
    time.sleep(1) #note dari sega, Gak usah di peduliin cuma buat "Stop" dikirim sebagai byte sendiri
    s.send(b"Stop")

# Fungsi untuk mengunduh file dari server
def download_file(s, filename):
    s.send(f'DOWNLOAD {filename}'.encode()) #mengirim request download beserta filename
    data1 = s.recv(BUFFER_SIZE) #menerima size dari file
    file_size = struct.unpack('!I', data1)[0] #unpack data1 untuk mengambi size data untuk dijadikan buffer size
    data2 = s.recv(file_size) #menerima data dari server seukuran file_size
    if data2 == b'File not found': # jika tidak ditemukan
        print(f"File '{filename}' not found on the server.")
    else:
        with open(filename, 'wb') as file: #writebinary
            file.write(data2)
        print(f"File '{filename}' downloaded successfully.")

# Membuat objek socket klien
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))
client_ip = client_socket.getpeername()[0]

#perlu dijelaskan ini ngapain?
while True:
    print("1. List file")
    print("2. Upload file")
    print("3. Download file")
    print("4. Exit")
    choice = input("Enter your choice (1-4): ")

    if choice == '1':
        list_files(client_socket)
    elif choice == '2':
        filename = input("Masukkan nama file yang ingin di Upload: ")
        upload_file(client_socket, filename)
    elif choice == '3':
        filename = input("Masukkan nama file yang ingin di Downloa: ")
        download_file(client_socket, filename)
    elif choice == '4':
        client_socket.close()
        sys.exit()
    else:
        print("Budayakan Membaca!")
