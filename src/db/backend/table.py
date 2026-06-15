from typing import Any
from .errors import MissingColumnError, UnknownColumnError, InvalidDataError


class Table:
    def __init__(self, columns: tuple[str, ...], records: list[dict[str, Any]] | None = None) -> None:
        self.columns = columns
        self.records: list[dict[str, Any]] = []
        if records is not None:
            for record in records:
                self.insert_record(record)

    def _validate_record(self, record: dict[str, Any]) -> None:
        if "age" in record:
            age = record["age"]
            if isinstance(age, bool) or not isinstance(age, (int, float)):
                raise InvalidDataError("Возраст должен быть числом")
            if age < 0:
                raise InvalidDataError("Возраст должен быть неотрицательным")

        if "sex" in record:
            sex = record["sex"]
            if not isinstance(sex, str):
                raise InvalidDataError("Пол должен быть строкой")
            if not sex.isalpha():
                raise InvalidDataError("Пол должен содержать только буквы")

    def _check_unique_id(self, record: dict[str, Any], exclude_index: int | None = None) -> None:
        if "id" not in record:
            return
        new_id = record["id"]
        for idx, existing in enumerate(self.records):
            if exclude_index is not None and idx == exclude_index:
                continue
            if existing.get("id") == new_id:
                raise InvalidDataError(f"Запись с ID {new_id} уже существует")

    def insert_record(self, record: dict[str, Any]) -> None:
        missing = [c for c in self.columns if c not in record]
        if missing:
            raise MissingColumnError(f"Отсутствует поле '{missing[0]}' в записи")

        extra = [c for c in record if c not in self.columns]
        if extra:
            raise UnknownColumnError(f"Поле '{extra[0]}' не определено в структуре таблицы")

        self._validate_record(record)
        self._check_unique_id(record)
        self.records.append(record.copy())

    def select_records(self, **filters: Any) -> list[dict[str, Any]]:
        unknown = [k for k in filters if k not in self.columns]
        if unknown:
            raise UnknownColumnError(f"Поле '{unknown[0]}' не определено в структуре таблицы")

        if not filters:
            return [r.copy() for r in self.records]

        result = []
        for record in self.records:
            if all(record.get(k) == v for k, v in filters.items()):
                result.append(record.copy())
        return result

    def update_records(self, filters: dict[str, Any], new_values: dict[str, Any]) -> int:
        unknown_f = [k for k in filters if k not in self.columns]
        if unknown_f:
            raise UnknownColumnError(f"Поле '{unknown_f[0]}' не определено в структуре таблицы")

        unknown_v = [k for k in new_values if k not in self.columns]
        if unknown_v:
            raise UnknownColumnError(f"Поле '{unknown_v[0]}' не определено в структуре таблицы")

        self._validate_record(new_values)

        updated = 0
        for idx, record in enumerate(self.records):
            if not filters or all(record.get(k) == v for k, v in filters.items()):
                if "id" in new_values:
                    test_record = {**record, **new_values}
                    self._check_unique_id(test_record, exclude_index=idx)
                record.update(new_values)
                updated += 1
        return updated

    def delete_records(self, filters: dict[str, Any]) -> int:
        unknown = [k for k in filters if k not in self.columns]
        if unknown:
            raise UnknownColumnError(f"Поле '{unknown[0]}' не определено в структуре таблицы")

        initial = len(self.records)
        if not filters:
            self.records.clear()
        else:
            self.records = [r for r in self.records if not all(r.get(k) == v for k, v in filters.items())]
        return initial - len(self.records)

    def sort_records(self, field: str, reverse: bool = False) -> None:
        if field not in self.columns:
            raise UnknownColumnError(f"Поле '{field}' не определено в структуре таблицы")
        try:
            self.records.sort(key=lambda r: r.get(field), reverse=reverse)
        except TypeError:
            self.records.sort(key=lambda r: str(r.get(field)), reverse=reverse)
