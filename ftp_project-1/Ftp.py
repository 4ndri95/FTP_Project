import ftplib
import os
import logging

def setup_logging():
    logging.basicConfig(
        filename='ftp_downloader.log', 
        level=logging.DEBUG,  
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

class FTPDownloader:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.ftp = None

    def connect(self):
        try:
            self.ftp = ftplib.FTP("ftp.elektro.com.br")
            self.ftp.login(self.username, self.password)
            self.ftp.set_pasv(True)
            self.ftp.voidcmd("TYPE I")
            logging.info(f"Conectado ao servidor FTP com usuário {self.username}")
        except ftplib.error_perm as e:
            logging.error(f"Erro de permissão ao conectar ao servidor FTP com usuário {self.username}: {e}")
            raise
        except ftplib.error_temp as e:
            logging.error(f"Erro temporário ao conectar ao servidor FTP com usuário {self.username}: {e}")
            raise
        except Exception as e:
            logging.error(f"Erro inesperado ao conectar ao servidor FTP com usuário {self.username}: {e}")
            raise

    def disconnect(self):
        if self.ftp:
            self.ftp.quit()
            logging.info(f"Desconectado do servidor FTP com usuário {self.username}")

    def download_files(self, folder, base_folder):
        try:
            self.ftp.cwd(folder)
            files = self.ftp.nlst()
            transferred_files = 0
            downloaded_files = []  # Lista para armazenar arquivos baixados
            failed_downloads = []  # Lista para armazenar arquivos que falharam ao serem baixados

            for file in files:
                try:
                    file_name = file.encode('latin1').decode('utf-8') 
                except UnicodeDecodeError:
                    logging.warning(f"Erro ao decodificar o nome do arquivo: {file}. Ignorando.")
                    continue 

                if file_name.lower().endswith(".pdf"):
                    local_file_path = os.path.join(base_folder, file_name)
                    os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
                    try:
                        with open(local_file_path, "wb") as f:
                            self.ftp.retrbinary("RETR " + file_name, f.write)
                        transferred_files += 1
                        downloaded_files.append(file_name)  # Armazenar o arquivo baixado
                        logging.info(f"Arquivo {file_name} transferido com sucesso para {local_file_path}")
                    except OSError as e:
                        logging.error(f"Erro ao salvar o arquivo {file_name} na pasta {base_folder}: {e}")
                        failed_downloads.append(file_name)  # Adicionar à lista de falhas
                    except ftplib.error_perm as e:
                        logging.error(f"Erro de permissão ao tentar baixar o arquivo {file_name}: {e}")
                        failed_downloads.append(file_name)  # Adicionar à lista de falhas
                    except Exception as e:
                        logging.error(f"Erro inesperado ao tentar baixar o arquivo {file_name}: {e}")
                        failed_downloads.append(file_name)  # Adicionar à lista de falhas

            # Verifica se houve falhas e registra
            if failed_downloads:
                logging.error(f"Falha ao transferir os seguintes arquivos da pasta {folder} no FTP: {', '.join(failed_downloads)}")
                print(f"Falha ao transferir os seguintes arquivos da pasta {folder} no FTP: {', '.join(failed_downloads)}")

            return transferred_files, downloaded_files  # Retornar também a lista de arquivos baixados
        except ftplib.error_perm as e:
            logging.error(f"Erro ao acessar o diretório {folder}: {e}")
            return 0, []
        except ftplib.error_temp as e:
            logging.error(f"Erro temporário ao acessar o diretório {folder}: {e}")
            return 0, []
        except Exception as e:
            logging.error(f"Erro inesperado ao tentar baixar arquivos do diretório {folder}: {e}")
            return 0, []

    def delete_files(self, folder, files):
        try:
            self.ftp.cwd(folder)
            existing_files = self.ftp.nlst()  # Lista os arquivos existentes no diretório
            for file in files:
                if file in existing_files:  # Verifica se o arquivo existe
                    try:
                        self.ftp.delete(file)
                        logging.info(f"Arquivo {file} deletado com sucesso de {folder}")
                    except ftplib.error_perm as e:
                        logging.error(f"Erro ao deletar o arquivo {file} em {folder}: {e}")
                    except Exception as e:
                        logging.error(f"Erro inesperado ao tentar deletar o arquivo {file} em {folder}: {e}")
                else:
                    logging.warning(f"Arquivo {file} não encontrado em {folder}. Ignorando a tentativa de deleção.")
        except ftplib.error_perm as e:
            logging.error(f"Erro ao acessar o diretório {folder} para deletar arquivos: {e}")
        except ftplib.error_temp as e:
            logging.error(f"Erro temporário ao acessar o diretório {folder} para deletar arquivos: {e}")
        except Exception as e:
            logging.error(f"Erro inesperado ao tentar acessar o diretório {folder} para deletar arquivos: {e}")

    def process_files(self, folder, base_folder):
        if not os.path.exists(base_folder):
            logging.error(f"O diretório base {base_folder} não existe. Abortando o download.")
            return

        transferred_files, downloaded_files = self.download_files(folder, base_folder)
        if transferred_files > 0:
            self.delete_files(folder, downloaded_files) 

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.disconnect()

def main():
    setup_logging()

    ftp_servers = [
        {"username": "username", "password": "password"},
        {"username": "username", "password": "password"},
        {"username": "username", "password": "password"},
        {"username": "username", "password": "password"}
    ]

    ftp_folders = ["/directory_1", "/directory_2", "/directory_3"]
    base_folders = {
        "/directory_1": "//path//to//directory",
        "/directory_2": "//path//to//directory",
        "/directory_3": "//path//to//directory"
    }

    transferred_files_by_base_folder = {}

    for server in ftp_servers:
        with FTPDownloader(server["username"], server["password"]) as downloader:
            for folder in ftp_folders:
                transferred_files, downloaded_files = downloader.process_files(folder, base_folders[folder]) 
                
                transferred_files_by_base_folder[base_folders[folder]] = transferred_files_by_base_folder.get(base_folders[folder], 0) + transferred_files

    for base_folder, total_transferred_files in transferred_files_by_base_folder.items():
        logging.info(f"Transferidos {total_transferred_files} PDF(s) para a pasta {base_folder}")
        print(f"Transferidos {total_transferred_files} PDF(s) para a pasta {base_folder}")

if __name__ == "__main__":
    main()
