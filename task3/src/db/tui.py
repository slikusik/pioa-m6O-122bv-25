from .backend.memory import StudentDB
from .backend.errors import StudentDBError


class StudentTUI:
    def __init__(self):
        self.db = StudentDB()

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

    def _print_records(self, records: list[tuple[int, str, str, int, str]]) -> None:
        if not records:
            print("Записи не найдены.")
            return
        for r in records:
            print(f"  ID: {r[0]}, Имя: {r[1]}, Фамилия: {r[2]}, Возраст: {r[3]}, Пол: {r[4]}")

    def _add(self) -> None:
        print("\nДобавление записи")
        sid = self._read_int("id: ")
        fname = input("first_name: ").strip()
        sname = input("second_name: ").strip()
        age = self._read_int("age: ")
        sex = input("sex: ").strip()
        try:
            rec = self.db.create_record(sid, fname, sname, age, sex)
            print(f"Запись добавлена: {rec}")
        except StudentDBError as e:
            print(f"Ошибка: {e}")

    def _show_all(self) -> None:
        print("\nСписок записей")
        self._print_records(self.db.select_record())

    def _find(self) -> None:
        print("\nПоиск (Enter – пропустить поле)")
        sid = self._read_optional_int("id: ")
        fname = input("first_name: ").strip() or None
        sname = input("second_name: ").strip() or None
        age = self._read_optional_int("age: ")
        sex = input("sex: ").strip() or None
        records = self.db.select_record(student_id=sid, first_name=fname,
                                        second_name=sname, age=age, sex=sex)
        self._print_records(records)

    def _update(self) -> None:
        print("\nОбновление по фильтру")
        print("Введите условия поиска (Enter – пропустить):")
        sid = self._read_optional_int("id: ")
        fname = input("first_name: ").strip() or None
        sname = input("second_name: ").strip() or None
        age = self._read_optional_int("age: ")
        sex = input("sex: ").strip() or None
        print("Новые значения (Enter – не менять):")
        new_fname = input("new_first_name: ").strip() or None
        new_sname = input("new_second_name: ").strip() or None
        new_age = self._read_optional_int("new_age: ")
        new_sex = input("new_sex: ").strip() or None
        try:
            updated = self.db.update_record(
                student_id=sid, first_name=fname, second_name=sname,
                age=age, sex=sex,
                new_first_name=new_fname, new_second_name=new_sname,
                new_age=new_age, new_sex=new_sex,
            )
            print(f"Обновлено записей: {len(updated)}")
            self._print_records(updated)
        except StudentDBError as e:
            print(f"Ошибка: {e}")

    def _delete(self) -> None:
        print("\nУдаление по фильтру")
        print("Введите условия поиска (Enter – пропустить):")
        sid = self._read_optional_int("id: ")
        fname = input("first_name: ").strip() or None
        sname = input("second_name: ").strip() or None
        age = self._read_optional_int("age: ")
        sex = input("sex: ").strip() or None
        try:
            deleted = self.db.delete_record(
                student_id=sid, first_name=fname, second_name=sname,
                age=age, sex=sex,
            )
            print(f"Удалено записей: {len(deleted)}")
        except StudentDBError as e:
            print(f"Ошибка: {e}")

    def _sort(self) -> None:
        print("\nСортировка записей")
        print("Доступные поля: id, first_name, second_name, age, sex")
        field = input("Введите поле для сортировки: ").strip()
        asc_input = input("По возрастанию? (д/н): ").strip().lower()

        reverse = asc_input not in ("д", "да", "y", "yes", "1")

        try:
            self.db.sort_records(field, reverse)
            print("Записи отсортированы.")
            self._show_all()
        except StudentDBError as e:
            print(f"Ошибка: {e}")

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
