from .backend.file import FileDatabase, CsvDatabase
from .backend.memory import MemoryDatabase


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
        except Exception:
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

    def _validate_age(self, age: int) -> bool:
        if age < 0:
            print("Ошибка: Поле age не может быть отрицательным.")
            return False
        return True

    def _validate_sex(self, sex: str) -> bool:
        if not sex.isalpha():
            print("Ошибка: Поле sex должно содержать только буквы.")
            return False
        return True

    def _matches_filters(self, record: dict, filters: dict) -> bool:
        for key, value in filters.items():
            record_value = record.get(key)
            if record_value is None:
                return False
            if str(record_value) != str(value):
                return False
        return True

    def _add(self) -> None:
        print("\nДобавление записи")
        sid = self._read_int("id: ")
        fname = input("first_name: ").strip()
        sname = input("second_name: ").strip()
        age = self._read_int("age: ")
        sex = input("sex: ").strip()

        if not self._validate_age(age):
            return
        if not self._validate_sex(sex):
            return

        all_records = self.db.select_records("students")
        for record in all_records:
            if str(record.get("id")) == str(sid):
                print(f"Ошибка: Студент с ID {sid} уже существует.")
                return

        try:
            self.db.insert_record("students", {
                "id": sid,
                "first_name": fname,
                "second_name": sname,
                "age": age,
                "sex": sex
            })
            print("Запись добавлена!")
        except Exception as e:
            print(f"Ошибка: {e}")

    def _show_all(self) -> None:
        print("\nСписок записей")
        self._print_records(self.db.select_records("students"))

    def _find(self) -> None:
        print("\nПоиск (Enter – пропустить поле)")
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

        records = self.db.select_records("students", **filters)
        self._print_records(records)

    def _update(self) -> None:
        print("\nОбновление по фильтру")
        print("Введите условия поиска (Enter – пропустить):")
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

        if not filters:
            print("Ошибка: укажите хотя бы одно поле для поиска.")
            return

        table = self.db._load_table("students")
        matching_records = [r for r in table.records if self._matches_filters(r, filters)]
        if not matching_records:
            print("Записи не найдены.")
            return

        print(f"Найдено записей: {len(matching_records)}")
        self._print_records(matching_records)

        print("\nНовые значения (Enter – не менять):")
        new_fname = input("new_first_name: ").strip() or None
        new_sname = input("new_second_name: ").strip() or None
        new_age = self._read_optional_int("new_age: ")
        new_sex = input("new_sex: ").strip() or None

        if new_age is not None and not self._validate_age(new_age):
            return
        if new_sex is not None and not self._validate_sex(new_sex):
            return

        updated_count = 0
        for record in table.records:
            if self._matches_filters(record, filters):
                if new_fname is not None:
                    record["first_name"] = new_fname
                if new_sname is not None:
                    record["second_name"] = new_sname
                if new_age is not None:
                    record["age"] = new_age
                if new_sex is not None:
                    record["sex"] = new_sex
                updated_count += 1

        self.db._save_table("students", table)
        print(f"Обновлено записей: {updated_count}")

    def _delete(self) -> None:
        print("\nУдаление по фильтру")
        print("Введите условия поиска (Enter – пропустить):")
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

        if not filters:
            print("Ошибка: укажите хотя бы одно поле для удаления.")
            return

        table = self.db._load_table("students")
        indices_to_delete = [i for i, record in enumerate(table.records) if self._matches_filters(record, filters)]

        if not indices_to_delete:
            print("Записи не найдены.")
            return

        print(f"Найдено записей для удаления: {len(indices_to_delete)}")
        for i in indices_to_delete:
            r = table.records[i]
            print(f"  ID: {r.get('id')}, Имя: {r.get('first_name')}, Фамилия: {r.get('second_name')}")

        # ВАЛИДАЦИЯ: требуем явного ввода "д" или "н"
        while True:
            confirm = input("Удалить? (д/н): ").strip().lower()
            if confirm in ("д", "н", "y", "n", "yes", "no", "1", "0"):
                break
            print("Ошибка: введите 'д' (да) или 'н' (нет).")

        if confirm not in ("д", "y", "yes", "1"):
            print("Удаление отменено.")
            return

        for i in reversed(indices_to_delete):
            table.records.pop(i)

        self.db._save_table("students", table)
        print(f"Удалено записей: {len(indices_to_delete)}")

    def _sort(self) -> None:
        print("\nСортировка записей")
        print("Доступные поля: id, first_name, second_name, age, sex")
        field = input("Введите поле для сортировки: ").strip()

        if field not in ("id", "first_name", "second_name", "age", "sex"):
            print("Ошибка: неизвестное поле.")
            return

        # ВАЛИДАЦИЯ: требуем явного ввода "д" или "н"
        while True:
            asc_input = input("По возрастанию? (д/н): ").strip().lower()
            if asc_input in ("д", "н", "y", "n", "yes", "no", "1", "0"):
                break
            print("Ошибка: введите 'д' (да) или 'н' (нет).")

        reverse = asc_input not in ("д", "y", "yes", "1")

        table = self.db._load_table("students")
        try:
            table.records.sort(key=lambda r: r[field], reverse=reverse)
        except TypeError:
            table.records.sort(key=lambda r: str(r[field]), reverse=reverse)

        self.db._save_table("students", table)
        print("Записи отсортированы.")
        self._print_records(table.records)

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
