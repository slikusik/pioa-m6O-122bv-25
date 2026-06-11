import tempfile
import os
import unittest
from src.db.backend.file import FileDatabase, CsvDatabase
from src.db.backend.errors import TableNotFoundError, TableAlreadyExistsError, InvalidStorageDataError


class TestFileDatabase(unittest.TestCase):
    def test_data_saved_between_instances(self):
        with tempfile.TemporaryDirectory() as directory:
            db1 = FileDatabase(directory)
            db1.create_table("students", ("id", "name"))
            db1.insert_record("students", {"id": 1, "name": "Иван"})

            db2 = FileDatabase(directory)
            records = db2.select_records("students")
            self.assertEqual(records, [{"id": 1, "name": "Иван"}])

    def test_select_with_filters(self):
        with tempfile.TemporaryDirectory() as directory:
            db = FileDatabase(directory)
            db.create_table("students", ("id", "name"))
            db.insert_record("students", {"id": 1, "name": "Иван"})
            db.insert_record("students", {"id": 2, "name": "Мария"})
            records = db.select_records("students", name="Мария")
            self.assertEqual(records, [{"id": 2, "name": "Мария"}])

    def test_select_missing_table(self):
        with tempfile.TemporaryDirectory() as directory:
            db = FileDatabase(directory)
            with self.assertRaises(TableNotFoundError):
                db.select_records("students")

    def test_create_table_already_exists(self):
        with tempfile.TemporaryDirectory() as directory:
            db = FileDatabase(directory)
            db.create_table("students", ("id",))
            with self.assertRaises(TableAlreadyExistsError):
                db.create_table("students", ("id",))

    def test_invalid_json(self):
        with tempfile.TemporaryDirectory() as directory:
            with open(os.path.join(directory, "students.json"), "w") as f:
                f.write("{bad json")
            db = FileDatabase(directory)
            with self.assertRaises(InvalidStorageDataError):
                db.select_records("students")


class TestCsvDatabase(unittest.TestCase):
    def test_data_saved_between_instances(self):
        with tempfile.TemporaryDirectory() as directory:
            db1 = CsvDatabase(directory)
            db1.create_table("students", ("id", "name"))
            db1.insert_record("students", {"id": 1, "name": "Иван"})

            db2 = CsvDatabase(directory)
            records = db2.select_records("students")
            # CSV хранит всё как строки
            self.assertEqual(records, [{"id": "1", "name": "Иван"}])

    def test_select_with_filters(self):
        with tempfile.TemporaryDirectory() as directory:
            db = CsvDatabase(directory)
            db.create_table("students", ("id", "name"))
            db.insert_record("students", {"id": 1, "name": "Иван"})
            db.insert_record("students", {"id": 2, "name": "Мария"})
            records = db.select_records("students", name="Мария")
            # CSV хранит всё как строки
            self.assertEqual(records, [{"id": "2", "name": "Мария"}])

    def test_select_missing_table(self):
        with tempfile.TemporaryDirectory() as directory:
            db = CsvDatabase(directory)
            with self.assertRaises(TableNotFoundError):
                db.select_records("students")

    def test_create_table_already_exists(self):
        with tempfile.TemporaryDirectory() as directory:
            db = CsvDatabase(directory)
            db.create_table("students", ("id",))
            with self.assertRaises(TableAlreadyExistsError):
                db.create_table("students", ("id",))
