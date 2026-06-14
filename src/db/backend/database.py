from abc import ABC, abstractmethod
from typing import Any
from .errors import TableAlreadyExistsError
from .table import Table


class Database(ABC):
    """Общий интерфейс базы данных."""

    def create_table(self, table_name: str, columns: tuple[str, ...]) -> None:
        if self._table_exists(table_name):
            raise TableAlreadyExistsError(
                f"Таблица '{table_name}' уже существует."
            )

        self._save_table(table_name, Table(columns))

    def insert_record(self, table_name: str, record: dict[str, Any]) -> None:
        table = self._load_table(table_name)
        table.insert_record(record)
        self._save_table(table_name, table)

    def select_records(self, table_name: str, **filters: Any) -> list[dict[str, Any]]:
        table = self._load_table(table_name)
        return table.select_records(**filters)

    def update_records(self, table_name: str, filters: dict[str, Any], new_values: dict[str, Any]) -> int:
        table = self._load_table(table_name)
        updated_count = table.update_records(filters, new_values)
        self._save_table(table_name, table)
        return updated_count

    def delete_records(self, table_name: str, filters: dict[str, Any]) -> int:
        table = self._load_table(table_name)
        deleted_count = table.delete_records(filters)
        self._save_table(table_name, table)
        return deleted_count

    def sort_records(self, table_name: str, field: str, reverse: bool = False) -> None:
        table = self._load_table(table_name)
        table.sort_records(field, reverse)
        self._save_table(table_name, table)

    @abstractmethod
    def _table_exists(self, table_name: str) -> bool:
        """Проверяет наличие таблицы."""

    @abstractmethod
    def _load_table(self, table_name: str) -> Table:
        """Загружает таблицу."""

    @abstractmethod
    def _save_table(self, table_name: str, table: Table) -> None:
        """Сохраняет таблицу."""
