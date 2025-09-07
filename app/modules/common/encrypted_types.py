"""
Кастомные типы SQLAlchemy для автоматического шифрования/расшифровки данных
"""

from typing import Optional, Any
from sqlalchemy import TypeDecorator, String
from sqlalchemy.engine import Dialect

from .encryption import encrypt_personal_data, decrypt_personal_data


class EncryptedString(TypeDecorator):
    """
    Кастомный тип SQLAlchemy для автоматического шифрования/расшифровки строк
    """

    impl = String
    cache_ok = True  # Разрешаем кэширование типа

    def __init__(self, length: Optional[int] = None, **kwargs):
        """
        Инициализация зашифрованного строкового типа

        Args:
            length: Максимальная длина поля (рекомендуется увеличить для зашифрованных данных)
        """
        # Увеличиваем длину поля для зашифрованных данных
        # Зашифрованные данные обычно в 2-3 раза длиннее оригинала
        if length:
            self.target_length = length
            actual_length = length * 3
        else:
            self.target_length = None
            actual_length = 500  # Значение по умолчанию для зашифрованных данных

        super().__init__(length=actual_length, **kwargs)

    def process_bind_param(
        self, value: Optional[str], dialect: Dialect
    ) -> Optional[str]:
        """
        Обработка данных при записи в БД (шифрование)

        Args:
            value: Значение для записи
            dialect: Диалект БД

        Returns:
            Зашифрованное значение
        """
        if value is not None:
            return encrypt_personal_data(value)
        return value

    def process_result_value(
        self, value: Optional[str], dialect: Dialect
    ) -> Optional[str]:
        """
        Обработка данных при чтении из БД (расшифровка)

        Args:
            value: Значение из БД
            dialect: Диалект БД

        Returns:
            Расшифрованное значение
        """
        if value is not None:
            return decrypt_personal_data(value)
        return value

    def copy(self, **kw: Any) -> "EncryptedString":
        """Создание копии типа"""
        return self.__class__(length=self.target_length, **kw)


class EncryptedIIN(EncryptedString):
    """
    Специализированный тип для ИИН с дополнительной валидацией
    """

    cache_ok = True

    def __init__(self, **kwargs):
        # ИИН состоит из 12 цифр, но зашифрованный будет намного длиннее
        super().__init__(length=12, **kwargs)

    def copy(self, **kw: Any) -> "EncryptedIIN":
        """Создание копии типа"""
        return EncryptedIIN(**kw)

    def process_bind_param(
        self, value: Optional[str], dialect: Dialect
    ) -> Optional[str]:
        """
        Обработка ИИН при записи с дополнительной валидацией
        """
        if value is not None:
            # Можно добавить дополнительную валидацию ИИН здесь
            value = value.strip()
            if len(value) != 12 or not value.isdigit():
                # Логируем предупреждение, но не блокируем операцию
                from loguru import logger

                logger.warning(f"Некорректный формат ИИН: {len(value)} символов")

        return super().process_bind_param(value, dialect)


class EncryptedPersonName(EncryptedString):
    """
    Специализированный тип для имен и фамилий
    """

    cache_ok = True

    def __init__(self, **kwargs):
        # Имена обычно не превышают 50 символов
        super().__init__(length=50, **kwargs)

    def copy(self, **kw: Any) -> "EncryptedPersonName":
        """Создание копии типа"""
        return EncryptedPersonName(**kw)

    def process_bind_param(
        self, value: Optional[str], dialect: Dialect
    ) -> Optional[str]:
        """
        Обработка имен при записи с нормализацией
        """
        if value is not None:
            # Нормализуем имя: убираем лишние пробелы, приводим к правильному регистру
            value = value.strip()
            if value:
                value = value.title()  # Первая буква заглавная

        return super().process_bind_param(value, dialect)
