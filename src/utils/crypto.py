import logging
from cryptography.fernet import Fernet

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [UTILS-CRYPTO] - %(message)s')

class CryptoHelper:
    """
    Classe utilitária responsável por cifrar e decifrar comunicações
    utilizando criptografia simétrica Fernet (AES).
    """
    def __init__(self, key: bytes) -> None:
        self.cipher = Fernet(key)

    def encrypt_data(self, data: bytes) -> bytes:
        """Cifra dados em bytes retornando um token criptografado."""
        try:
            return self.cipher.encrypt(data)
        except Exception as e:
            logging.error(f"Erro ao cifrar dados: {e}")
            return data

    def decrypt_data(self, encrypted_data: bytes) -> bytes:
        """Decifra um token Fernet retornando os bytes originais."""
        try:
            return self.cipher.decrypt(encrypted_data)
        except Exception as e:
            logging.error(f"Erro ao decifrar dados: {e}")
            return b""

    @staticmethod
    def generate_new_key() -> bytes:
        """Gera uma chave simétrica válida de forma aleatória e segura."""
        return Fernet.generate_key()