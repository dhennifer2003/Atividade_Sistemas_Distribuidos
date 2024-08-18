import rpyc
import os
from datetime import datetime, timedelta

class ServicoTransferenciaArquivos(rpyc.Service):
    def __init__(self):
        self.interesses = {}  # Dicionário para armazenar interesses dos clientes

    def on_connect(self, conn): #chamado automaticamente quando o cliente se conecta no servidor 
        print("Cliente conectado") #console pra registrar que conectou

    def on_disconnect(self, conn): #esse método é chamado quando o cliente se desconecta do servidor
        print("Cliente desconectado")

    def exposed_fazer_upload_arquivo(self, nome_arquivo, dados): #exposed é um método que pode ser chamado remotamente pelo cliente
        try:
            with open(nome_arquivo, 'wb') as f: # Abre o arquivo e escreve os dados (conteudo) fornecidos pelo cliente
                f.write(dados)
            print(f"Arquivo {nome_arquivo} enviado com sucesso")
            self._notificar_clientes_interessados(nome_arquivo) # Após o upload, notifica os clientes que tenham registrado interesse neste arquivo.
            return f"Arquivo {nome_arquivo} enviado com sucesso"
        except Exception as e:
            print(f"Erro durante o envio do arquivo: {e}") #mensagem mostrada ao cliente em caso de erro
            return f"Falha ao enviar o arquivo {nome_arquivo}: {e}"

    def exposed_listar_arquivos(self): #lista todos os arquivos disponíveis no diretório atual do servidor
        try:
            arquivos = os.listdir('.')
            return [f for f in arquivos if os.path.isfile(f)] #retorna uma lista com os nomes dos arquivos
        except Exception as e:
            print(f"Erro ao listar arquivos: {e}")
            return [] 

    def exposed_fazer_download_arquivo(self, nome_arquivo): #permite a um cliente baixar um arquivo do servidor
        try:
            # Verifica se o arquivo existe no servidor
            if not os.path.exists(nome_arquivo):
                raise FileNotFoundError(f"Arquivo {nome_arquivo} não existe")

            with open(nome_arquivo, 'rb') as f:
                dados = f.read()
            return dados
        except Exception as e:
            print(f"Erro durante o download do arquivo: {e}")
            raise e  # Relevantar a exceção para informar o cliente

    def exposed_registrar_interesse(self, nome_arquivo, ref_cliente, duracao): #cliente registra interesse e é notificado quando o arquivo em especifico estiver disponível no servidor
        try:
            # é calculado o tempo de expiração do interesse com base na duração fornecida
            tempo_expiracao = datetime.now() + timedelta(segundos=duracao)
            #feito o registro do interesse no dicionário `interesses`
            self.interesses[nome_arquivo] = (ref_cliente, tempo_expiracao)
            print(f"Interesse registrado para o arquivo {nome_arquivo} até {tempo_expiracao}")
            return f"Interesse registrado para o arquivo {nome_arquivo} até {tempo_expiracao}"
        except Exception as e:
            print(f"Erro ao registrar interesse por {nome_arquivo}: {e}")
            return f"Falha ao registrar interesse por {nome_arquivo}: {e}"

    def exposed_cancelar_interesse(self, nome_arquivo): #cliente pode cacncelar o interesse em um determinado arquivo
        try:
            #verifica se o arquivo de interesse existe e o remove.
            if nome_arquivo in self.interesses:
                del self.interesses[nome_arquivo]
                print(f"Interesse pelo arquivo {nome_arquivo} cancelado")
                return f"Interesse pelo arquivo {nome_arquivo} cancelado"
            else:
                return f"Nenhum interesse encontrado para o arquivo {nome_arquivo}"
        except Exception as e:
            print(f"Erro ao cancelar interesse por {nome_arquivo}: {e}")
            return f"Falha ao cancelar interesse por {nome_arquivo}: {e}"

    def _notificar_clientes_interessados(self, nome_arquivo): #Método interno que notifica os clientes que registraram interesse em um arquivo específico quando ele se torna disponível no servidor
        try:
            #Verifica se há algum interesse registrado para o arquivo:
            if nome_arquivo in self.interesses:
                # Verifica se o interesse ainda é válido (não expirou):
                ref_cliente, tempo_expiracao = self.interesses[nome_arquivo]
                if datetime.now() <= tempo_expiracao:
                    try:
                        # Tenta notificar o cliente sobre a disponibilidade do arquivo
                        ref_cliente.root.notificar_arquivo_disponivel(nome_arquivo)
                        print(f"Notificação enviada ao cliente para o arquivo {nome_arquivo}")
                    except Exception as e:
                        # Se a notificação falhar, registra o erro
                        print(f"Falha ao notificar o cliente sobre o arquivo {nome_arquivo}: {e}")
                del self.interesses[nome_arquivo]
        except Exception as e:
            print(f"Erro ao notificar clientes interessados: {e}")

if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer
    try:
        servidor = ThreadedServer(ServicoTransferenciaArquivos, port=18861) #servidor e é criado nessa porta, sendo ele multithread
        print("Servidor iniciado na porta 18861")
        servidor.start()
    except Exception as e:
        print(f"Falha ao iniciar o servidor: {e}")
