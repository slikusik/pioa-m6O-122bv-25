import unittest
from src.db.backend.memory import MemoryDatabase
from src.db.backend.errors import TableAlreadyExistsError, MissingColumnError, TableNotFoundError

class TestMemoryDatabase(unittest.TestCase):
    def setUp(self):
        self.db = MemoryDatabase()
        self.db.create_table("students", ("id", "first_name", "second_name", "age", "sex"))

    def test_insert_and_select(self):
        self.db.insert_record("students", {"id": 1, "first_name": "Иван", "second_name": "Иванов", "age": 20, "sex": "м"})
        records = self.db.select_records("students")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["first_name"], "Иван")

    def test_filter(self):
        self.db.insert_record("students", {"id": 1, "first_name": "Иван", "second_name": "Иванов", "age": 20, "sex": "м"})
        self.db.insert_record("students", {"id": 2, "first_name": "Мария", "second_name": "Петрова", "age": 21, "sex": "ж"})
        records = self.db.select_records("students", first_name="Мария")
        self.assertEqual(len(records), 1)

    def test_missing_column_error(self):
        with self.assertRaises(MissingColumnError):
            self.db.insert_record("students", {"id": 1, "first_name": "Тест"})

    def test_missing_table_error(self):
        with self.assertRaises(TableNotFoundError):
            self.db.select_records("nonexistent_table")
