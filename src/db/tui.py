from .backend.file import FileDatabase, CsvDatabase
from .backend.memory import MemoryDatabase
from .backend.errors import (
    TableAlreadyExistsError,
    InvalidDataError,
    TableNotFoundError,
    MissingColumnError,
    UnknownColumnError,
    InvalidStorageDataError,
)


class StudentTUI:
    def __init__(self) -> None:
        print("Выберите тип базы данных:")
        print("1. In-memory")
        print("2. File database (JSON)")
        print("3. File database (CSV)")

        choice = input("Введите номер: ").strip()
        if choice == "2":
            self.db = FileDatabase()
        elif choice == "3":
            self.db = CsvDatabase()
        else:
            self.db = MemoryDatabase()

        try:
            self.db.create_table("students", ("id", "first_name", "second_name", "age", "sex"))
        except TableAlreadyExistsError:
            pass

    def _print_menu(self) -> None:
        print("\n=== База студентов ===")
        print("1. Добавить запись")
        print("2. Показать все записи")
        print("3. Найти записи")
        print("4. Обновить записи")
        print("5. Удалить записи")
        print("6. Сортировать записи")
        print("0. Выход")

    def _read_int(self, prompt: str) -> int:
        while True:
            raw = input(prompt).strip()
            try:
                return int(raw)
            except ValueError:
                print("Ошибка: введите целое число.")

    def _read_optional_int(self, prompt: str) -> int | None:
        while True:
            raw = input(prompt).strip()
            if raw == "":
                return None
            try:
                return int(raw)
            except ValueError:
                print("Ошибка: введите целое число или оставьте поле пустым.")

    def _print_records(self, records: list[dict]) -> None:
        if not records:
            print("Записи не найдены.")
            return
        for r in records:
            print(f"  ID: {r['id']}, Имя: {r['first_name']}, Фамилия: {r['second_name']}, Возраст: {r['age']}, Пол: {r['sex']}")

    def _build_filters(self) -> dict:
        sid = self._read_optional_int("id: ")
        fname = input("first_name: ").strip() or None
        sname = input("second_name: ").strip() or None
        age = self._read_optional_int("age: ")
        sex = input("sex: ").strip() or None

        filters = {}
        if sid is not None:
            filters["id"] = sid
        if fname is not None:
            filters["first_name"] = fname
        if sname is not None:
            filters["second_name"] = sname
        if age is not None:
            filters["age"] = age
        if sex is not None:
            filters["sex"] = sex

        return filters

    def _handle_db_error(self, error: Exception) -> None:
        if isinstance(error, InvalidDataError):
            print(f"Ошибка валидации: {error}")
        elif isinstance(error, (MissingColumnError, UnknownColumnError)):
            print(f"Ошибка структуры: {error}")
        elif isinstance(error, TableNotFoundError):
            print(f"Таблица не найдена: {error}")
        elif isinstance(error, InvalidStorageDataError):
            print(f"Ошибка чтения данных: {error}")
        else:
            print(f"Ошибка: {error}")

    def _add(self) -> None:
        print("\nДобавление записи")
        sid = self._read_int("id: ")
        fname = input("first_name: ").strip()
        sname = input("second_name: ").strip()
        age = self._read_int("age: ")
        sex = input("sex: ").strip()

        try:
            self.db.insert_record("students", {
                "id": sid,
                "first_name": fname,
                "second_name": sname,
                "age": age,
                "sex": sex,
            })
            print("Запись добавлена")
        except (InvalidDataError, MissingColumnError, UnknownColumnError, TableNotFoundError, InvalidStorageDataError) as error:
            self._handle_db_error(error)

    def _show_all(self) -> None:
        print("\nСписок записей")
        try:
            records = self.db.select_records("students")
            self._print_records(records)
        except (TableNotFoundError, InvalidStorageDataError) as error:
            self._handle_db_error(error)

    def _find(self) -> None:
        print("\nПоиск (Enter - пропустить поле)")
        filters = self._build_filters()
        try:
            records = self.db.select_records("students", **filters)
            self._print_records(records)
        except (UnknownColumnError, TableNotFoundError, InvalidStorageDataError) as error:
            self._handle_db_error(error)

    def _update(self) -> None:
        print("\nОбновление по фильтру")
        print("Введите условия поиска (Enter - пропустить):")
        filters = self._build_filters()

        if not filters:
            print("Ошибка: укажите хотя бы одно поле для поиска.")
            return

        try:
            matching = self.db.select_records("students", **filters)
        except (UnknownColumnError, TableNotFoundError, InvalidStorageDataError) as error:
            self._handle_db_error(error)
            return

        if not matching:
            print("Записи не найдены.")
            return

        print(f"Найдено записей: {len(matching)}")
        self._print_records(matching)

        print("\nНовые значения (Enter - не менять):")
        new_fname = input("new_first_name: ").strip() or None
        new_sname = input("new_second_name: ").strip() or None
        new_age = self._read_optional_int("new_age: ")
        new_sex = input("new_sex: ").strip() or None

        new_values = {}
        if new_fname is not None:
            new_values["first_name"] = new_fname
        if new_sname is not None:
            new_values["second_name"] = new_sname
        if new_age is not None:
            new_values["age"] = new_age
        if new_sex is not None:
            new_values["sex"] = new_sex

        if not new_values:
            print("Новые значения не заданы. Обновление отменено.")
            return

        try:
            count = self.db.update_records("students", filters, new_values)
            print(f"Обновлено записей: {count}")
        except (InvalidDataError, UnknownColumnError, TableNotFoundError, InvalidStorageDataError) as error:
            self._handle_db_error(error)

    def _delete(self) -> None:
        print("\nУдаление по фильтру")
        print("Введите условия поиска (Enter - пропустить):")
        filters = self._build_filters()

        if not filters:
            print("Ошибка: укажите хотя бы одно поле для удаления.")
            return

        try:
            matching = self.db.select_records("students", **filters)
        except (UnknownColumnError, TableNotFoundError, InvalidStorageDataError) as error:
            self._handle_db_error(error)
            return

        if not matching:
            print("Записи не найдены.")
            return

        print(f"Найдено записей для удаления: {len(matching)}")
        for r in matching:
            print(f"  ID: {r.get('id')}, Имя: {r.get('first_name')}, Фамилия: {r.get('second_name')}")

        while True:
            confirm = input("Удалить? (д/н): ").strip().lower()
            if confirm in ("д", "н", "y", "n", "yes", "no", "1", "0"):
                break
            print("Ошибка: введите 'д' (да) или 'н' (нет).")

        if confirm not in ("д", "y", "yes", "1"):
            print("Удаление отменено.")
            return

        try:
            count = self.db.delete_records("students", filters)
            print(f"Удалено записей: {count}")
        except (UnknownColumnError, TableNotFoundError, InvalidStorageDataError) as error:
            self._handle_db_error(error)

    def _sort(self) -> None:
        print("\nСортировка записей")
        print("Доступные поля: id, first_name, second_name, age, sex")
        field = input("Введите поле для сортировки: ").strip()

        if field not in ("id", "first_name", "second_name", "age", "sex"):
            print("Ошибка: неизвестное поле.")
            return

        while True:
            asc = input("По возрастанию? (д/н): ").strip().lower()
            if asc in ("д", "н", "y", "n", "yes", "no", "1", "0"):
                break
            print("Ошибка: введите 'д' (да) или 'н' (нет).")

        reverse = asc not in ("д", "y", "yes", "1")

        try:
            self.db.sort_records("students", field, reverse=reverse)
            print("Записи отсортированы.")
            records = self.db.select_records("students")
            self._print_records(records)
        except (UnknownColumnError, TableNotFoundError, InvalidStorageDataError) as error:
            self._handle_db_error(error)

    def run(self) -> None:
        while True:
            self._print_menu()
            action = input("Выберите действие: ").strip()
            if action == "1":
                self._add()
            elif action == "2":
                self._show_all()
            elif action == "3":
                self._find()
            elif action == "4":
                self._update()
            elif action == "5":
                self._delete()
            elif action == "6":
                self._sort()
            elif action == "0":
                print("Выход из программы.")
                break
            else:
                print("Неизвестная команда. Повторите ввод.")


def run() -> None:
    tui = StudentTUI()
    tui.run()
