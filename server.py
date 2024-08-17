import rpyc
import os
from datetime import datetime, timedelta

class ServicoTransferenciaArquivos(rpyc.Service):
    def __init__(self):
        self.interesses = {}  # Dicionário para armazenar interesses dos clientes

    def on_connect(self, conn):
        print("Cliente conectado")

    def on_disconnect(self, conn):
        print("Cliente desconectado")

    def exposed_fazer_upload_arquivo(self, nome_arquivo, dados):
        try:
            with open(nome_arquivo, 'wb') as f:
                f.write(dados)
            print(f"Arquivo {nome_arquivo} enviado com sucesso")
            self._notificar_clientes_interessados(nome_arquivo)
            return f"Arquivo {nome_arquivo} enviado com sucesso"
        except Exception as e:
            print(f"Erro durante o envio do arquivo: {e}")
            return f"Falha ao enviar o arquivo {nome_arquivo}: {e}"

    def exposed_listar_arquivos(self):
        try:
            arquivos = os.listdir('.')
            return [f for f in arquivos if os.path.isfile(f)]
        except Exception as e:
            print(f"Erro ao listar arquivos: {e}")
            return []

    def exposed_fazer_download_arquivo(self, nome_arquivo):
        try:
            if not os.path.exists(nome_arquivo):
                raise FileNotFoundError(f"Arquivo {nome_arquivo} não existe")

            with open(nome_arquivo, 'rb') as f:
                dados = f.read()
            return dados
        except Exception as e:
            print(f"Erro durante o download do arquivo: {e}")
            raise e  # Relevantar a exceção para informar o cliente

    def exposed_registrar_interesse(self, nome_arquivo, ref_cliente, duracao):
        try:
            tempo_expiracao = datetime.now() + timedelta(segundos=duracao)
            self.interesses[nome_arquivo] = (ref_cliente, tempo_expiracao)
            print(f"Interesse registrado para o arquivo {nome_arquivo} até {tempo_expiracao}")
            return f"Interesse registrado para o arquivo {nome_arquivo} até {tempo_expiracao}"
        except Exception as e:
            print(f"Erro ao registrar interesse por {nome_arquivo}: {e}")
            return f"Falha ao registrar interesse por {nome_arquivo}: {e}"

    def exposed_cancelar_interesse(self, nome_arquivo):
        try:
            if nome_arquivo in self.interesses:
                del self.interesses[nome_arquivo]
                print(f"Interesse pelo arquivo {nome_arquivo} cancelado")
                return f"Interesse pelo arquivo {nome_arquivo} cancelado"
            else:
                return f"Nenhum interesse encontrado para o arquivo {nome_arquivo}"
        except Exception as e:
            print(f"Erro ao cancelar interesse por {nome_arquivo}: {e}")
            return f"Falha ao cancelar interesse por {nome_arquivo}: {e}"

    def _notificar_clientes_interessados(self, nome_arquivo):
        try:
            if nome_arquivo in self.interesses:
                ref_cliente, tempo_expiracao = self.interesses[nome_arquivo]
                if datetime.now() <= tempo_expiracao:
                    try:
                        ref_cliente.root.notificar_arquivo_disponivel(nome_arquivo)
                        print(f"Notificação enviada ao cliente para o arquivo {nome_arquivo}")
                    except Exception as e:
                        print(f"Falha ao notificar o cliente sobre o arquivo {nome_arquivo}: {e}")
                del self.interesses[nome_arquivo]
        except Exception as e:
            print(f"Erro ao notificar clientes interessados: {e}")

if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer
    try:
        servidor = ThreadedServer(ServicoTransferenciaArquivos, port=18861)
        print("Servidor iniciado na porta 18861")
        servidor.start()
    except Exception as e:
        print(f"Falha ao iniciar o servidor: {e}")
