import json
import csv
from pathlib import Path
from .database import Database
from .errors import InvalidStorageDataError, TableNotFoundError
from .table import Table

NUMERIC_COLUMNS = {"id", "age"}


class FileDatabase(Database):
    def __init__(self, directory: str = "data") -> None:
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def _table_exists(self, table_name: str) -> bool:
        return self._get_table_path(table_name).exists()

    def _load_table(self, table_name: str) -> Table:
        table_path = self._get_table_path(table_name)
        if not table_path.exists():
            raise TableNotFoundError(f"Таблица '{table_name}' не существует")

        try:
            with table_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError as error:
            raise InvalidStorageDataError("Файл таблицы содержит некорректный JSON") from error
        except OSError as error:
            raise InvalidStorageDataError(f"Ошибка чтения файла: {error}") from error

        return self._deserialize_table(data)

    def _save_table(self, table_name: str, table: Table) -> None:
        table_path = self._get_table_path(table_name)
        try:
            with table_path.open("w", encoding="utf-8") as file:
                json.dump(self._serialize_table(table), file, ensure_ascii=False, indent=2)
        except OSError as error:
            raise InvalidStorageDataError(f"Ошибка записи файла: {error}") from error

    def _get_table_path(self, table_name: str) -> Path:
        return self.directory / f"{table_name}.json"

    def _serialize_table(self, table: Table) -> dict:
        return {
            "columns": list(table.columns),
            "records": [record.copy() for record in table.records],
        }

    def _deserialize_table(self, data: dict) -> Table:
        if not isinstance(data, dict):
            raise InvalidStorageDataError("Файл должен содержать JSON-объект")
        if "columns" not in data:
            raise InvalidStorageDataError("Отсутствует поле 'columns'")
        if "records" not in data:
            raise InvalidStorageDataError("Отсутствует поле 'records'")
        if not isinstance(data["columns"], list):
            raise InvalidStorageDataError("Поле 'columns' должно быть списком")
        if not isinstance(data["records"], list):
            raise InvalidStorageDataError("Поле 'records' должно быть списком")
        for col in data["columns"]:
            if not isinstance(col, str):
                raise InvalidStorageDataError(f"Элемент 'columns' должен быть строкой, а не {type(col).__name__}")
        for idx, record in enumerate(data["records"]):
            if not isinstance(record, dict):
                raise InvalidStorageDataError(f"Запись {idx} должна быть словарём, а не {type(record).__name__}")
        
        columns = tuple(data["columns"])
        records = data["records"]
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
            raise TableNotFoundError(f"Таблица '{table_name}' не существует")

        try:
            with table_path.open("r", encoding="utf-8-sig", newline="") as file:
                reader = csv.DictReader(file, delimiter=';')
                if reader.fieldnames is None:
                    raise InvalidStorageDataError("CSV-файл пуст или не содержит заголовков")
                columns = tuple(reader.fieldnames)
                records = list(reader)
        except csv.Error as error:
            raise InvalidStorageDataError(f"Ошибка парсинга CSV-файла: {error}") from error
        except OSError as error:
            raise InvalidStorageDataError(f"Ошибка чтения CSV-файла: {error}") from error

        for record in records:
            for column in columns:
                if column in NUMERIC_COLUMNS and column in record:
                    try:
                        record[column] = int(record[column])
                    except (ValueError, TypeError):
                        pass

        return Table(columns, records)

    def _save_table(self, table_name: str, table: Table) -> None:
        table_path = self._get_table_path(table_name)
        try:
            with table_path.open("w", encoding="utf-8-sig", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=table.columns, delimiter=';')
                writer.writeheader()
                writer.writerows(table.records)
        except OSError as error:
            raise InvalidStorageDataError(f"Ошибка записи CSV-файла: {error}") from error

    def _get_table_path(self, table_name: str) -> Path:
        return self.directory / f"{table_name}.csv"
