import unittest
from src.db.backend.memory import StudentDB
from src.db.backend.errors import RecordNotFoundError, RecordAlreadyExistsError, InvalidDataError


class TestStudentDB(unittest.TestCase):
    def setUp(self):
        self.db = StudentDB()

    def test_create_record_success(self):
        rec = self.db.create_record(1, "Иван", "Иванов", 20, "м")
        self.assertEqual(rec, (1, "Иван", "Иванов", 20, "м"))
        self.assertEqual(len(self.db.select_record()), 1)

    def test_create_record_negative_age(self):
        with self.assertRaises(InvalidDataError):
            self.db.create_record(1, "Иван", "Иванов", -5, "м")

    def test_create_record_duplicate_id(self):
        self.db.create_record(1, "Иван", "Иванов", 20, "м")
        with self.assertRaises(RecordAlreadyExistsError):
            self.db.create_record(1, "Петр", "Петров", 21, "м")

    def test_create_record_trims_whitespace(self):
        rec = self.db.create_record(1, "  Иван  ", "  Иванов  ", 20, "  м  ")
        self.assertEqual(rec, (1, "Иван", "Иванов", 20, "м"))

    def test_create_record_invalid_sex_numbers(self):
        with self.assertRaises(InvalidDataError):
            self.db.create_record(1, "Иван", "Иванов", 20, "1")

    def test_create_record_invalid_sex_symbols(self):
        with self.assertRaises(InvalidDataError):
            self.db.create_record(1, "Иван", "Иванов", 20, "m@le")

    # --- Тесты для select_record ---
    def test_select_all_records(self):
        self.db.create_record(1, "Иван", "Иванов", 20, "м")
        self.db.create_record(2, "Петр", "Петров", 21, "м")
        self.assertEqual(len(self.db.select_record()), 2)

    def test_select_by_id(self):
        self.db.create_record(1, "Иван", "Иванов", 20, "м")
        self.db.create_record(2, "Петр", "Петров", 21, "м")
        records = self.db.select_record(student_id=1)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0][0], 1)

    def test_select_by_name(self):
        self.db.create_record(1, "Иван", "Иванов", 20, "м")
        self.db.create_record(2, "Иван", "Петров", 21, "м")
        self.assertEqual(len(self.db.select_record(first_name="Иван")), 2)

    def test_select_no_results(self):
        self.db.create_record(1, "Иван", "Иванов", 20, "м")
        self.assertEqual(len(self.db.select_record(student_id=999)), 0)

    def test_select_empty_db(self):
        self.assertEqual(len(self.db.select_record()), 0)

    # --- Тесты для update_record ---
    def test_update_success(self):
        self.db.create_record(1, "Иван", "Иванов", 20, "м")
        updated = self.db.update_record(student_id=1, new_first_name="Петр")
        self.assertEqual(updated[0][1], "Петр")

    def test_update_multiple_fields(self):
        self.db.create_record(1, "Иван", "Иванов", 20, "м")
        updated = self.db.update_record(student_id=1, new_first_name="Петр", new_age=25)
        self.assertEqual(updated[0][1], "Петр")
        self.assertEqual(updated[0][3], 25)

    def test_update_no_matching_records(self):
        self.db.create_record(1, "Иван", "Иванов", 20, "м")
        with self.assertRaises(RecordNotFoundError):
            self.db.update_record(student_id=999, new_first_name="Петр")

    def test_delete_success(self):
        self.db.create_record(1, "Иван", "Иванов", 20, "м")
        self.assertEqual(len(self.db.delete_record(student_id=1)), 1)
        self.assertEqual(len(self.db.select_record()), 0)

    def test_delete_no_matching_records(self):
        self.db.create_record(1, "Иван", "Иванов", 20, "м")
        with self.assertRaises(RecordNotFoundError):
            self.db.delete_record(student_id=999)

    def test_delete_empty_filter(self):
        self.db.create_record(1, "Иван", "Иванов", 20, "м")
        self.assertIsNone(self.db.delete_record())

    def test_sort_records_ascending(self):
        self.db.create_record(3, "Иван", "Иванов", 20, "м")
        self.db.create_record(1, "Петр", "Петров", 21, "м")
        self.db.create_record(2, "Анна", "Сидорова", 22, "ж")

        self.db.sort_records("id")
        records = self.db.select_record()
        self.assertEqual([r[0] for r in records], [1, 2, 3])

    def test_sort_records_descending(self):
        self.db.create_record(1, "Иван", "Иванов", 20, "м")
        self.db.create_record(2, "Петр", "Петров", 25, "м")
        self.db.create_record(3, "Анна", "Сидорова", 22, "ж")

        self.db.sort_records("age", reverse=True)
        records = self.db.select_record()
        self.assertEqual([r[3] for r in records], [25, 22, 20])

    def test_sort_records_invalid_field(self):
        with self.assertRaises(InvalidDataError):
            self.db.sort_records("invalid_field")


if __name__ == "__main__":
    unittest.main()
