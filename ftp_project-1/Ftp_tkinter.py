import ftplib
import os
import logging
import tkinter as tk
from tkinter import messagebox, simpledialog

# Configuração do logging
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
        except ftplib.all_errors as e:
            logging.error(f"Erro ao conectar ao servidor FTP com usuário {self.username}: {e}")
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
            downloaded_files = []
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
                        downloaded_files.append(file_name)
                        logging.info(f"Arquivo {file_name} transferido com sucesso para {local_file_path}")
                    except Exception as e:
                        logging.error(f"Erro ao salvar o arquivo {file_name} na pasta {base_folder}: {e}")
            return transferred_files, downloaded_files
        except ftplib.error_perm as e:
            logging.error(f"Erro ao acessar o diretório {folder}: {e}")
            return 0, []
        except Exception as e:
            logging.error(f"Erro inesperado ao tentar baixar arquivos do diretório {folder}: {e}")
            return 0, []

    def delete_files(self, folder, files):
        try:
            self.ftp.cwd(folder)
            existing_files = self.ftp.nlst()
            for file in files:
                if file in existing_files:
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
        except Exception as e:
            logging.error(f"Erro inesperado ao tentar acessar o diretório {folder} para deletar arquivos: {e}")

    def process_files(self, folder, base_folder):
        transferred_files, downloaded_files = self.download_files(folder, base_folder)
        if transferred_files > 0:
            self.delete_files(folder, downloaded_files)

def run_ftp_downloader():
    ftp_servers = [
        {"username": "toi_guaruja", "password": "tgua9987"},
        {"username": "toi_atibaia", "password": "tatb9987"},
        {"username": "toi_rioclaro", "password": "trcl9987"},
        {"username": "toi_votuporanga", "password": "tvtp9987"},
        {"username": "toi_piracicaba", "password": "tpir9987"},
        {"username": "toi_taubate", "password": "ttau9987"},
    ]

    base_folder = simpledialog.askstring("Pasta de Download", "Digite o caminho da pasta onde os arquivos devem ser salvos:")
    if not base_folder:
        messagebox.showerror("Erro", "O caminho da pasta não pode ser vazio.")
        return

    for server in ftp_servers:
        try:
            downloader = FTPDownloader(server["username"], server["password"])
            downloader.connect()
            downloader.process_files("/" + server["username"], base_folder)
            downloader.disconnect()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar o servidor {server['username']}: {e}")

    messagebox.showinfo("Concluído", "Processamento concluído!")

# Criação da interface gráfica
def main():
    root = tk.Tk()
    root.title("FTP Downloader")

    label = tk.Label(root, text="Clique no botão abaixo para iniciar o download dos arquivos.")
    label.pack(pady=10)

    start_button = tk.Button(root, text="Iniciar Download", command=run_ftp_downloader)
    start_button.pack(pady=20)

    root.geometry("400x200")
    root.mainloop()

if __name__ == "__main__":
    main()