import sys
import os
import logging

# Ajuste do path para importar os módulos corretamente
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core import CommandAndControlServer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')

def main():
    print("="*50)
    print("      INICIALIZADOR DO SERVIDOR C2 SECURE")
    print("="*50)
    
    # Solicita as configurações de rede interativamente
    host_input = input("[+] Digite o IP de escuta (Padrão: 0.0.0.0): ").strip()
    if not host_input:
        host_input = "0.0.0.0"  # Escuta em todas as interfaces se deixar em branco
        
    port_input = input("[+] Digite a porta de escuta (Padrão: 4444): ").strip()
    if not port_input:
        port_input = "4444"
        
    try:
        port = int(port_input)
    except ValueError:
        logging.error("A porta deve ser um número inteiro válido.")
        sys.exit(1)

    # Inicializa o servidor com os parâmetros fornecidos via input
    server = CommandAndControlServer(host=host_input, port=port)
    server.start()

if __name__ == "__main__":
    main()