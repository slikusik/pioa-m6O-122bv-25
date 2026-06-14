import unittest
from src.db.backend.memory import MemoryDatabase
from src.db.backend.errors import TableNotFoundError, MissingColumnError, UnknownColumnError


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

    def test_filter_by_single_field(self):
        self.db.insert_record("students", {
            "id": 1, "first_name": "Иван", "second_name": "Иванов", "age": 20, "sex": "м"
        })
        self.db.insert_record("students", {
            "id": 2, "first_name": "Мария", "second_name": "Петрова", "age": 21, "sex": "ж"
        })
        records = self.db.select_records("students", first_name="Мария")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["id"], 2)

    def test_filter_by_multiple_fields(self):
        self.db.insert_record("students", {
            "id": 1, "first_name": "Иван", "second_name": "Иванов", "age": 20, "sex": "м"
        })
        self.db.insert_record("students", {
            "id": 2, "first_name": "Иван", "second_name": "Сидоров", "age": 25, "sex": "м"
        })
        records = self.db.select_records("students", first_name="Иван", age=20)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["second_name"], "Иванов")

    def test_insert_missing_column_error(self):
        with self.assertRaises(MissingColumnError):
            self.db.insert_record("students", {"id": 1})

    def test_insert_unknown_column_error(self):
        with self.assertRaises(UnknownColumnError):
            self.db.insert_record("students", {
                "id": 1, "first_name": "Иван", "second_name": "Иванов",
                "age": 20, "sex": "м", "unknown": "value"
            })

    def test_select_unknown_filter_error(self):
        with self.assertRaises(UnknownColumnError):
            self.db.select_records("students", unknown_field="test")

    def test_select_missing_table_error(self):
        with self.assertRaises(TableNotFoundError):
            self.db.select_records("nonexistent")

    def test_update_records(self):
        self.db.insert_record("students", {
            "id": 1, "first_name": "Иван", "second_name": "Иванов", "age": 20, "sex": "м"
        })
        updated_count = self.db.update_records("students", {"id": 1}, {"age": 21})
        self.assertEqual(updated_count, 1)
        records = self.db.select_records("students", id=1)
        self.assertEqual(records[0]["age"], 21)

    def test_delete_records(self):
        self.db.insert_record("students", {
            "id": 1, "first_name": "Иван", "second_name": "Иванов", "age": 20, "sex": "м"
        })
        self.db.insert_record("students", {
            "id": 2, "first_name": "Мария", "second_name": "Петрова", "age": 21, "sex": "ж"
        })
        deleted_count = self.db.delete_records("students", {"id": 1})
        self.assertEqual(deleted_count, 1)
        remaining = self.db.select_records("students")
        self.assertEqual(len(remaining), 1)
        self.assertEqual(remaining[0]["id"], 2)

    def test_sort_records(self):
        self.db.insert_record("students", {
            "id": 3, "first_name": "Анна", "second_name": "Сидорова", "age": 22, "sex": "ж"
        })
        self.db.insert_record("students", {
            "id": 1, "first_name": "Иван", "second_name": "Иванов", "age": 20, "sex": "м"
        })
        self.db.insert_record("students", {
            "id": 2, "first_name": "Мария", "second_name": "Петрова", "age": 21, "sex": "ж"
        })
        self.db.sort_records("students", "age")
        records = self.db.select_records("students")
        self.assertEqual([r["age"] for r in records], [20, 21, 22])
