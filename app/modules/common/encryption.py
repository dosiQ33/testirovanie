import base64
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from loguru import logger

from app.config import settings


class DataEncryption:
    """Класс для шифрования/расшифровки персональных данных"""

    def __init__(self):
        self._fernet = None
        self._init_encryption()

    def _init_encryption(self):
        """Инициализация шифрования"""
        try:
            password = settings.SECRET_KEY.encode()
            salt = b"coc_personal_data_salt"

            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password))
            self._fernet = Fernet(key)

        except Exception as e:
            logger.error(f"Ошибка инициализации шифрования: {e}")
            raise

    def encrypt(self, data: Optional[str]) -> Optional[str]:
        """
        Шифрование данных

        Args:
            data: Строка для шифрования

        Returns:
            Зашифрованная строка в base64 или None
        """
        if not data or data.strip() == "":
            return data

        try:
            encrypted_data = self._fernet.encrypt(data.encode("utf-8"))
            return base64.urlsafe_b64encode(encrypted_data).decode("utf-8")
        except Exception as e:
            logger.error(f"Ошибка шифрования данных: {e}")
            return data

    def decrypt(self, encrypted_data: Optional[str]) -> Optional[str]:
        """
        Расшифровка данных

        Args:
            encrypted_data: Зашифрованная строка в base64

        Returns:
            Расшифрованная строка или None
        """
        if not encrypted_data or encrypted_data.strip() == "":
            return encrypted_data

        try:
            if not self._is_encrypted_format(encrypted_data):
                return encrypted_data

            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode("utf-8"))
            decrypted_data = self._fernet.decrypt(decoded_data)
            return decrypted_data.decode("utf-8")
        except Exception as e:
            logger.warning(
                f"Ошибка расшифровки данных (возможно, данные не зашифрованы): {e}"
            )
            return encrypted_data

    def _is_encrypted_format(self, data: str) -> bool:
        """
        Проверяет, похожи ли данные на зашифрованный формат

        Args:
            data: Строка для проверки

        Returns:
            True если похоже на зашифрованные данные
        """
        try:
            decoded = base64.urlsafe_b64decode(data.encode("utf-8"))
            return len(decoded) > 40
        except:
            return False


data_encryption = DataEncryption()


def encrypt_personal_data(data: Optional[str]) -> Optional[str]:
    """Функция-обертка для шифрования"""
    return data_encryption.encrypt(data)


def decrypt_personal_data(data: Optional[str]) -> Optional[str]:
    """Функция-обертка для расшифровки"""
    return data_encryption.decrypt(data)
