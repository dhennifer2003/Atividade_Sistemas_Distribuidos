import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import rpyc
import os

class ClienteArquivos(rpyc.Service):
    def on_connect(self, conn):
        print("Conectado ao servidor")

    def on_disconnect(self, conn):
        print("Desconectado do servidor")

    def exposed_notificar_arquivo_disponivel(self, nome_arquivo):
        print(f"Notificação: O arquivo '{nome_arquivo}' está agora disponível!")

class ClienteArquivosApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Cliente de Transferência de Arquivos")

        self.conn = rpyc.connect("localhost", 18861, service=ClienteArquivos)

        self.label_status = tk.Label(master, text="Bem-vindo ao Cliente de Transferência de Arquivos")
        self.label_status.pack(pady=10)

        self.botao_upload = tk.Button(master, text="Enviar Arquivo", command=self.fazer_upload_arquivo)
        self.botao_upload.pack(pady=5)

        self.botao_listar = tk.Button(master, text="Listar Arquivos", command=self.listar_arquivos)
        self.botao_listar.pack(pady=5)

        self.botao_download = tk.Button(master, text="Baixar Arquivo", command=self.fazer_download_arquivo)
        self.botao_download.pack(pady=5)

        self.botao_registrar = tk.Button(master, text="Registrar Interesse", command=self.registrar_interesse)
        self.botao_registrar.pack(pady=5)

        self.botao_cancelar = tk.Button(master, text="Cancelar Interesse", command=self.cancelar_interesse)
        self.botao_cancelar.pack(pady=5)

        self.botao_sair = tk.Button(master, text="Sair", command=self.master.quit)
        self.botao_sair.pack(pady=10)

    def fazer_upload_arquivo(self):
        caminho_arquivo = filedialog.askopenfilename(title="Selecione o arquivo para enviar")
        if not caminho_arquivo:
            return

        with open(caminho_arquivo, 'rb') as f:
            dados = f.read()

        nome_arquivo = os.path.basename(caminho_arquivo)
        resposta = self.conn.root.fazer_upload_arquivo(nome_arquivo, dados)
        messagebox.showinfo("Upload de Arquivo", resposta)

    def listar_arquivos(self):
        arquivos = self.conn.root.listar_arquivos()
        messagebox.showinfo("Arquivos Disponíveis", "\n".join(arquivos))

    def fazer_download_arquivo(self):
        nome_arquivo = simpledialog.askstring("Baixar Arquivo", "Digite o nome do arquivo para baixar:")
        if not nome_arquivo:
            return

        destino = filedialog.asksaveasfilename(title="Salvar Arquivo Como", initialfile=nome_arquivo)
        if not destino:
            return
        
        try:
            dados = self.conn.root.fazer_download_arquivo(nome_arquivo)
            with open(destino, 'wb') as f:
                f.write(dados)
            messagebox.showinfo("Download de Arquivo", f"Arquivo '{nome_arquivo}' baixado com sucesso!")
        except FileNotFoundError as e:
            messagebox.showerror("Erro", str(e))

    def registrar_interesse(self):
        nome_arquivo = simpledialog.askstring("Registrar Interesse", "Digite o nome do arquivo:")
        if not nome_arquivo:
            return

        duracao = simpledialog.askinteger("Duração", "Digite a duração do interesse (segundos):")
        if not duracao:
            return

        resposta = self.conn.root.registrar_interesse(nome_arquivo, self.conn, duracao)
        messagebox.showinfo("Registrar Interesse", resposta)

    def cancelar_interesse(self):
        nome_arquivo = simpledialog.askstring("Cancelar Interesse", "Digite o nome do arquivo:")
        if not nome_arquivo:
            return

        resposta = self.conn.root.cancelar_interesse(nome_arquivo)
        messagebox.showinfo("Cancelar Interesse", resposta)

    def on_closing(self):
        self.conn.close()
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ClienteArquivosApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
