"""Тесты автономной работы бэкенда (без участия TUI)."""
import unittest
from src.db.backend.memory import MemoryDatabase
from src.db.backend.errors import MissingColumnError, UnknownColumnError, InvalidDataError


class TestMemoryDatabase(unittest.TestCase):
    def setUp(self):
        self.db = MemoryDatabase()
        self.db.create_table("students", ("id", "first_name", "second_name", "age", "sex"))

    def test_insert_and_select(self):
        self.db.insert_record("students", {
            "id": 1, "first_name": "Иван", "second_name": "Иванов", "age": 20, "sex": "м"
        })
        records = self.db.select_records("students")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["first_name"], "Иван")

    def test_backend_rejects_negative_age(self):
        with self.assertRaises(InvalidDataError):
            self.db.insert_record("students", {
                "id": 1, "first_name": "Иван", "second_name": "Иванов", "age": -5, "sex": "м"
            })

    def test_backend_rejects_invalid_sex(self):
        with self.assertRaises(InvalidDataError):
            self.db.insert_record("students", {
                "id": 1, "first_name": "Иван", "second_name": "Иванов", "age": 20, "sex": "123"
            })

    def test_backend_rejects_duplicate_id_on_insert(self):
        self.db.insert_record("students", {
            "id": 1, "first_name": "Иван", "second_name": "Иванов", "age": 20, "sex": "м"
        })
        with self.assertRaises(InvalidDataError):
            self.db.insert_record("students", {
                "id": 1, "first_name": "Пётр", "second_name": "Петров", "age": 25, "sex": "м"
            })

    def test_backend_rejects_duplicate_id_on_update(self):
        self.db.insert_record("students", {"id": 1, "first_name": "Иван", "second_name": "Иванов", "age": 20, "sex": "м"})
        self.db.insert_record("students", {"id": 2, "first_name": "Мария", "second_name": "Петрова", "age": 21, "sex": "ж"})
        with self.assertRaises(InvalidDataError):
            self.db.update_records("students", {"id": 2}, {"id": 1})

    def test_backend_missing_column(self):
        with self.assertRaises(MissingColumnError):
            self.db.insert_record("students", {"id": 1})

    def test_backend_unknown_column(self):
        with self.assertRaises(UnknownColumnError):
            self.db.insert_record("students", {
                "id": 1, "first_name": "Иван", "second_name": "Иванов", "age": 20, "sex": "м", "extra": "data"
            })

    def test_sort_records(self):
        self.db.insert_record("students", {"id": 3, "first_name": "Анна", "second_name": "Сидорова", "age": 22, "sex": "ж"})
        self.db.insert_record("students", {"id": 1, "first_name": "Иван", "second_name": "Иванов", "age": 20, "sex": "м"})
        self.db.sort_records("students", "age")
        records = self.db.select_records("students")
        self.assertEqual([r["age"] for r in records], [20, 22])
