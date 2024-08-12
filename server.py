# server.py
import rpyc
import os
from datetime import datetime, timedelta

class FileTransferService(rpyc.Service):
    def __init__(self):
        self.interests = {}  # Dicionário para armazenar interesses dos clientes

    def on_connect(self, conn):
        print("Client connected")

    def on_disconnect(self, conn):
        print("Client disconnected")

    def exposed_upload_file(self, filename, data):
        with open(filename, 'wb') as f:
            f.write(data)
        print(f"File {filename} uploaded successfully")
        self._notify_interested_clients(filename)
        return f"File {filename} uploaded successfully"

    def exposed_list_files(self):
        files = os.listdir('.')
        return [f for f in files if os.path.isfile(f)]

    def exposed_download_file(self, filename):
        if not os.path.exists(filename):
            raise FileNotFoundError(f"File {filename} does not exist")

        with open(filename, 'rb') as f:
            data = f.read()
        return data

    def exposed_register_interest(self, filename, client_ref, duration):
        expiry_time = datetime.now() + timedelta(seconds=duration)
        self.interests[filename] = (client_ref, expiry_time)
        print(f"Interest registered for file {filename} until {expiry_time}")
        return f"Interest registered for file {filename} until {expiry_time}"

    def exposed_cancel_interest(self, filename):
        if filename in self.interests:
            del self.interests[filename]
            print(f"Interest for file {filename} cancelled")
            return f"Interest for file {filename} cancelled"
        else:
            return f"No interest found for file {filename}"

    def _notify_interested_clients(self, filename):
        if filename in self.interests:
            client_ref, expiry_time = self.interests[filename]
            if datetime.now() <= expiry_time:
                try:
                    client_ref.root.notify_file_available(filename)
                    print(f"Notification sent to client for file {filename}")
                except Exception as e:
                    print(f"Failed to notify client for file {filename}: {e}")
            del self.interests[filename]

if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer
    server = ThreadedServer(FileTransferService, port=18861)
    print("Server started on port 18861")
    server.start()
