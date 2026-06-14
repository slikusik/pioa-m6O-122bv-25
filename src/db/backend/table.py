from typing import Any

from .errors import MissingColumnError, UnknownColumnError


class Table:
    def __init__(self, columns: tuple[str, ...], records: list[dict[str, Any]] | None = None) -> None:
        self.columns = columns
        self.records: list[dict[str, Any]] = []

        if records is not None:
            for record in records:
                self.insert_record(record)

    def insert_record(self, record: dict[str, Any]) -> None:
        missing_columns = [column for column in self.columns if column not in record]
        if missing_columns:
            raise MissingColumnError(
                f"Отсутствует поле '{missing_columns[0]}' в записи."
            )

        extra_columns = [column for column in record if column not in self.columns]
        if extra_columns:
            raise UnknownColumnError(
                f"Поле '{extra_columns[0]}' не определено в структуре таблицы."
            )

        self.records.append(record.copy())

    def select_records(self, **filters: Any) -> list[dict[str, Any]]:
        unknown_filters = [key for key in filters if key not in self.columns]
        if unknown_filters:
            raise UnknownColumnError(
                f"Поле '{unknown_filters[0]}' не определено в структуре таблицы."
            )

        if not filters:
            return [record.copy() for record in self.records]

        result: list[dict[str, Any]] = []
        for record in self.records:
            if all(record.get(key) == value for key, value in filters.items()):
                result.append(record.copy())

        return result

    def update_records(self, filters: dict[str, Any], new_values: dict[str, Any]) -> int:
        unknown_filters = [key for key in filters if key not in self.columns]
        if unknown_filters:
            raise UnknownColumnError(f"Поле '{unknown_filters[0]}' не определено в структуре таблицы.")

        unknown_values = [key for key in new_values if key not in self.columns]
        if unknown_values:
            raise UnknownColumnError(f"Поле '{unknown_values[0]}' не определено в структуре таблицы.")

        updated_count = 0
        for record in self.records:
            if not filters or all(record.get(key) == value for key, value in filters.items()):
                record.update(new_values)
                updated_count += 1

        return updated_count

    def delete_records(self, filters: dict[str, Any]) -> int:
        unknown_filters = [key for key in filters if key not in self.columns]
        if unknown_filters:
            raise UnknownColumnError(f"Поле '{unknown_filters[0]}' не определено в структуре таблицы.")

        initial_count = len(self.records)
        if not filters:
            self.records.clear()
        else:
            self.records = [
                r for r in self.records
                if not all(r.get(key) == value for key, value in filters.items())
            ]

        return initial_count - len(self.records)

    def sort_records(self, field: str, reverse: bool = False) -> None:
        if field not in self.columns:
            raise UnknownColumnError(f"Поле '{field}' не определено в структуре таблицы.")

        try:
            self.records.sort(key=lambda r: r.get(field), reverse=reverse)
        except TypeError:
            self.records.sort(key=lambda r: str(r.get(field)), reverse=reverse)
