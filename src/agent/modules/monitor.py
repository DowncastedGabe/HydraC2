import threading
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [MODULE-MONITOR] - %(message)s')

class BackgroundMonitor:
    """
    Módulo responsável por executar telemetria e coleta de dados em segundo plano
    utilizando concorrência (Threads) de forma isolada.
    """
    def __init__(self, interval: int = 10) -> None:
        self.interval: int = interval
        self.is_monitoring: bool = False
        self._thread: Optional[threading.Thread] = None

    def _loop(self) -> None:
        """Loop interno que roda estritamente dentro da Thread secundária."""
        while self.is_monitoring:
            try:
                # Espaço reservado para lógicas acadêmicas (ex: checar novos processos, capturar teclas)
                logging.info("Executando checagem periódica de telemetria no alvo...")
                time.sleep(self.interval)
            except Exception as e:
                logging.error(f"Erro no loop de monitoramento: {e}")
                self.is_monitoring = False

    def start(self) -> None:
        """Inicia a execução assíncrona do módulo."""
        if self.is_monitoring:
            return

        self.is_monitoring = True
        # Configuração de Engenharia: daemon=True impede que o processo fique preso na memória
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        logging.info("Módulo de monitoramento acoplado e iniciado em background.")

    def stop(self) -> None:
        """Para o loop de monitoramento de forma segura."""
        self.is_monitoring = False
        logging.info("Módulo de monitoramento finalizado.")