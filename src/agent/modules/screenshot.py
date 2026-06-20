import io
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [MODULE-SCREENSHOT] - %(message)s')

def take_screenshot() -> bytes:
    """Captura a tela e trata de forma dinâmica a ausência do módulo mss."""
    try:
        # Importação dinâmica em tempo de execução para evitar falhas no boot
        from mss import mss
        import mss.tools
        
        with mss() as sct:
            monitor = sct.monitors[1]
            screenshot = sct.grab(monitor)
            png_bytes = mss.tools.to_png(screenshot.rgb, screenshot.size)
            logging.info("[+] Captura de tela realizada com sucesso.")
            return png_bytes
            
    except ImportError:
        logging.error("[-] Erro: Dependência 'mss' não encontrada no sistema.")
        return b"[-] Erro: Dependencia externa 'mss' nao instalada no alvo."
    except Exception as e:
        logging.error(f"[-] Falha geral na captura: {e}")
        return f"[-] Erro na captura: {str(e)}".encode("utf-8")