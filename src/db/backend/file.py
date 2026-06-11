import json
import csv
from pathlib import Path

from .database import Database
from .errors import InvalidStorageDataError, TableNotFoundError
from .table import Table


class FileDatabase(Database):
    def __init__(self, directory: str = "data") -> None:
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def _table_exists(self, table_name: str) -> bool:
        return self._get_table_path(table_name).exists()

    def _load_table(self, table_name: str) -> Table:
        table_path = self._get_table_path(table_name)
        if not table_path.exists():
            raise TableNotFoundError(
                f"Таблица '{table_name}' не существует."
            )

        try:
            with table_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError as error:
            raise InvalidStorageDataError(
                "Файл таблицы содержит некорректный JSON."
            ) from error

        return self._deserialize_table(data)

    def _save_table(self, table_name: str, table: Table) -> None:
        table_path = self._get_table_path(table_name)

        with table_path.open("w", encoding="utf-8") as file:
            json.dump(
                self._serialize_table(table),
                file,
                ensure_ascii=False,
                indent=2,
            )

    def _get_table_path(self, table_name: str) -> Path:
        return self.directory / f"{table_name}.json"

    def _serialize_table(self, table: Table) -> dict:
        return {
            "columns": list(table.columns),
            "records": [record.copy() for record in table.records],
        }

    def _deserialize_table(self, data: dict) -> Table:
        if "columns" not in data or "records" not in data:
            raise InvalidStorageDataError(
                "Файл таблицы имеет некорректную структуру."
            )

        columns = tuple(data["columns"])
        records = data.get("records", [])
        return Table(columns, records)


class CsvDatabase(Database):
    def __init__(self, directory: str = "data") -> None:
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def _table_exists(self, table_name: str) -> bool:
        return self._get_table_path(table_name).exists()

    def _load_table(self, table_name: str) -> Table:
        table_path = self._get_table_path(table_name)
        if not table_path.exists():
            raise TableNotFoundError(
                f"Таблица '{table_name}' не существует."
            )

        try:
            with table_path.open("r", encoding="utf-8-sig", newline="") as file:
                reader = csv.DictReader(file, delimiter=';')
                columns = tuple(reader.fieldnames) if reader.fieldnames else ()
                records = list(reader)
        except Exception as error:
            raise InvalidStorageDataError(
                f"Ошибка чтения CSV-файла: {error}"
            ) from error

        return Table(columns, records)

    def _save_table(self, table_name: str, table: Table) -> None:
        table_path = self._get_table_path(table_name)

        with table_path.open("w", encoding="utf-8-sig", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=table.columns, delimiter=';')
            writer.writeheader()
            writer.writerows(table.records)

    def _get_table_path(self, table_name: str) -> Path:
        return self.directory / f"{table_name}.csv"
