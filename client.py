# client.py
import rpyc
import os

class FileClient(rpyc.Service):
    def on_connect(self, conn):
        print("Connected to server")

    def on_disconnect(self, conn):
        print("Disconnected from server")

    def exposed_notify_file_available(self, filename):
        print(f"Notification: The file '{filename}' is now available!")

def upload_file(client, filepath):
    with open(filepath, 'rb') as f:
        data = f.read()

    filename = os.path.basename(filepath)
    response = client.root.upload_file(filename, data)
    print(response)

def list_files(client):
    files = client.root.list_files()
    print("Available files:", files)

def download_file(client, filename, destination):
    try:
        data = client.root.download_file(filename)
        with open(destination, 'wb') as f:
            f.write(data)
        print(f"File '{filename}' downloaded successfully to '{destination}'")
    except FileNotFoundError as e:
        print(e)

def register_interest(client, filename, duration):
    response = client.root.register_interest(filename, client, duration)
    print(response)

def cancel_interest(client, filename):
    response = client.root.cancel_interest(filename)
    print(response)

if __name__ == "__main__":
    conn = rpyc.connect("localhost", 18861, service=FileClient)
    
    # Exemplo de upload de arquivo
    upload_file(conn, r"C:\Users\dhenn\Documents\teste.txt")
    
    # Exemplo de listagem de arquivos
    list_files(conn)
    
    # Exemplo de download de arquivo
    download_file(conn, "teste.txt", r"C:\Users\dhenn\Documents")

    # Registrar interesse em um arquivo
    register_interest(conn, "teste.txt", 60)

    # Cancelar interesse em um arquivo
    cancel_interest(conn, "teste.txt")

    conn.close()
