import tempfile
import os
import unittest
from src.db.backend.file import FileDatabase, CsvDatabase
from src.db.backend.errors import TableNotFoundError, TableAlreadyExistsError, InvalidStorageDataError


class TestFileDatabase(unittest.TestCase):
    """Тесты для JSON-реализации (6 тестов)."""

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.directory = self.tmp_dir.name

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_data_saved_between_instances(self):
        db1 = FileDatabase(self.directory)
        db1.create_table("students", ("id", "name"))
        db1.insert_record("students", {"id": 1, "name": "Иван"})
        db2 = FileDatabase(self.directory)
        records = db2.select_records("students")
        self.assertEqual(records, [{"id": 1, "name": "Иван"}])

    def test_select_with_filters(self):
        db = FileDatabase(self.directory)
        db.create_table("students", ("id", "name"))
        db.insert_record("students", {"id": 1, "name": "Иван"})
        db.insert_record("students", {"id": 2, "name": "Мария"})
        records = db.select_records("students", name="Мария")
        self.assertEqual(records, [{"id": 2, "name": "Мария"}])

    def test_select_missing_table(self):
        db = FileDatabase(self.directory)
        with self.assertRaises(TableNotFoundError):
            db.select_records("students")

    def test_create_table_already_exists(self):
        db = FileDatabase(self.directory)
        db.create_table("students", ("id",))
        with self.assertRaises(TableAlreadyExistsError):
            db.create_table("students", ("id",))

    def test_invalid_json(self):
        with open(os.path.join(self.directory, "students.json"), "w") as f:
            f.write("{bad json")
        db = FileDatabase(self.directory)
        with self.assertRaises(InvalidStorageDataError):
            db.select_records("students")

    def test_update_records_json(self):
        db = FileDatabase(self.directory)
        db.create_table("students", ("id", "name", "age"))
        db.insert_record("students", {"id": 1, "name": "Иван", "age": 20})
        updated_count = db.update_records("students", {"id": 1}, {"age": 21})
        self.assertEqual(updated_count, 1)
        records = db.select_records("students", id=1)
        self.assertEqual(records[0]["age"], 21)


class TestCsvDatabase(unittest.TestCase):
    """Тесты для CSV-реализации (7 тестов)."""

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.directory = self.tmp_dir.name

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_data_saved_between_instances(self):
        db1 = CsvDatabase(self.directory)
        db1.create_table("students", ("id", "name"))
        db1.insert_record("students", {"id": 1, "name": "Иван"})
        db2 = CsvDatabase(self.directory)
        records = db2.select_records("students")
        self.assertEqual(records, [{"id": 1, "name": "Иван"}])

    def test_select_with_filters(self):
        db = CsvDatabase(self.directory)
        db.create_table("students", ("id", "name"))
        db.insert_record("students", {"id": 1, "name": "Иван"})
        db.insert_record("students", {"id": 2, "name": "Мария"})
        records = db.select_records("students", name="Мария")
        self.assertEqual(records, [{"id": 2, "name": "Мария"}])

    def test_select_missing_table(self):
        db = CsvDatabase(self.directory)
        with self.assertRaises(TableNotFoundError):
            db.select_records("students")

    def test_create_table_already_exists(self):
        db = CsvDatabase(self.directory)
        db.create_table("students", ("id",))
        with self.assertRaises(TableAlreadyExistsError):
            db.create_table("students", ("id",))

    def test_csv_preserves_int_types(self):
        """Главный тест: CSV конвертирует id и age в int."""
        db = CsvDatabase(self.directory)
        db.create_table("students", ("id", "name", "age"))
        db.insert_record("students", {"id": 1, "name": "Иван", "age": 20})
        db2 = CsvDatabase(self.directory)
        records = db2.select_records("students")
        self.assertIsInstance(records[0]["id"], int)
        self.assertIsInstance(records[0]["age"], int)
        self.assertEqual(records[0]["id"], 1)
        self.assertEqual(records[0]["age"], 20)

    def test_csv_filter_by_int_after_reload(self):
        """Фильтрация по числу работает после перезагрузки CSV."""
        db1 = CsvDatabase(self.directory)
        db1.create_table("students", ("id", "name", "age"))
        db1.insert_record("students", {"id": 1, "name": "Иван", "age": 20})
        db1.insert_record("students", {"id": 2, "name": "Мария", "age": 21})
        db2 = CsvDatabase(self.directory)
        records = db2.select_records("students", id=1)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["name"], "Иван")

    def test_update_records_csv(self):
        db = CsvDatabase(self.directory)
        db.create_table("students", ("id", "name", "age"))
        db.insert_record("students", {"id": 1, "name": "Иван", "age": 20})
        updated_count = db.update_records("students", {"id": 1}, {"age": 21})
        self.assertEqual(updated_count, 1)
        db2 = CsvDatabase(self.directory)
        records = db2.select_records("students", id=1)
        self.assertEqual(records[0]["age"], 21)


if __name__ == "__main__":
    unittest.main()
