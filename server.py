import socket
import threading
import struct
import os
from datetime import datetime

# Konfigurasi server
IP = '192.168.104.133'  # IP server
PORT = 2023  # Port server
BUFFER_SIZE = 1024  # Ukuran buffer
DRIVE_FOLDER = 'Drive'  # Folder penyimpanan file
LOG_FILE = 'log.txt'  # Nama file untuk log

# Fungsi untuk menangani koneksi dari client
def handle_client(client_socket, addr):
    print(f"> Koneksi diterima dari {addr[0]}:{addr[1]}")
    while True: 
        request = client_socket.recv(BUFFER_SIZE).decode() #menerima request dari client
        
        if not request :#untuk perintah dari server yang bukan merupakan request seperti untuk menutup koneksi
            break
        
        if request == 'LIST':
            list_files(client_socket)
        elif request.startswith('UPLOAD'):
            upload_file(client_socket,  request.split()[1], request.split()[2], addr[0]) #[0] = tipe request, [1] = filename, [2] = size, addr[0] = alamat IP
        elif request.startswith('DOWNLOAD'):
            download_file(client_socket, request.split()[1], addr[0])#[0] = tipe request, [1] = filename, [2] = size, addr[0] = alamat IP

    client_socket.close()
    print(f"> Koneksi dari {addr[0]}:{addr[1]} ditutup")

# Fungsi untuk mengirim daftar file kepada client
def list_files(client_socket):
    files = os.listdir(DRIVE_FOLDER) #membaca isi folder
    files_str = "\n".join(files) #sambungin semuanya menjadi list
    client_socket.send(files_str.encode())#kirim ke client

# Fungsi untuk mengunggah file dari client ke server
def upload_file(client_socket, filename, size, client_ip):
    fz = int(size) #jadiin int
    file_path = os.path.join(DRIVE_FOLDER, filename) # sambungin folder dan name
    with open(file_path, 'wb') as file: #writebinary
        while True:
            data = client_socket.recv(fz) #terima data
            if data == b'Stop': #jika datanya malah bilang Stop ya stop lah
                break
            file.write(data) #write data yang diterima
    log_action(f"{client_ip} Upload - File: {filename}") #catat dia upload apa jangan-jangan 4NO!

# Fungsi untuk mengunduh file dari server ke client
def download_file(client_socket, filename, client_ip):
    try: #test dulu kalau filenya ada atau tidak
        file_path = os.path.join(DRIVE_FOLDER, filename) # sambungin folder dan name
        with open(file_path, 'rb') as file: #readbinary
            file_size = os.path.getsize(file_path) #ambil size file dan simpan ke file_size
            client_socket.send(struct.pack('!I', file_size)) #paketkan file size agar bisa dikirimkan lewat JNE
            data = file.read(file_size) #baca datanya
            while data:#KIRIM DAN BACA KIRIM DAN BACA sampai habis
                client_socket.send(data)
                data = file.read(file_size)
        log_action(f"{client_ip} Download - File: {filename}") #catat dia download apa 
    except FileNotFoundError: #kalau clientnya tolol atau typo kirimin file tidak ditemukan
        client_socket.send(b'File tidak ditemukan')

# Fungsi untuk mencatat tindakan dalam file log
def log_action(action):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S") #waktu dia lakukan aksi kapan?
    dl = dict()
    up = dict()
    with open(LOG_FILE, 'a') as log: # buka file log
        log.write(f"{action} - {timestamp}\n") #tulis kapan dia lakukan dan ngapain
    with open(LOG_FILE, 'r') as log: #buka file log
        for line in log: #read tiap baris
            text = line.split() # pisahkan
            if text[1] == "Download": # jika download
                dl[text[0]] = dl.get(text[0], 0) + 1 #kalau gak ngerti skill issue
            elif text[1] == "Upload": # jika upload
                up[text[0]] = up.get(text[0], 0) + 1 #kalau gak ngerti skill issue
    print(f"{action}")
    if dl:
        print("Download Terbanyak =", max(dl, key=lambda x: x[1])) #cari max dari dl dengan cara di balik antara key dan value untuk di max
    if up:
        print("Upload Terbanyak =", max(up, key=lambda x: x[1]),"\n") #cari max dari up dengan cara di balik antara key dan value untuk di max

# Inisialisasi socket server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((IP, PORT))
s.listen(5) #up to 5 koneksi

print(f"> Mendengarkan alamat {IP}:{PORT}")

# Menerima koneksi dari client secara bersamaan
while True:
    client, addr = s.accept()
    client_handler = threading.Thread(target=handle_client, args=(client, addr)) #inisialisasi Threading
    client_handler.start() #threading goes brrrrr...
