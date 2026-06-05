from .errors import RecordNotFoundError, RecordAlreadyExistsError, InvalidDataError

StudentRecord = tuple[int, str, str, int, str]


class StudentDB:
    def __init__(self) -> None:
        self._students: list[StudentRecord] = []

    def create_record(self, student_id: int, first_name: str, second_name: str,
                      age: int, sex: str) -> StudentRecord:
        """Создание новой записи."""
        if age < 0:
            raise InvalidDataError("Поле age не может быть отрицательным.")

        sex_clean = str(sex).strip()
        if not sex_clean or not sex_clean.isalpha():
            raise InvalidDataError("Поле sex должно содержать только буквы (например: м, ж).")

        if any(rec[0] == student_id for rec in self._students):
            raise RecordAlreadyExistsError(f"Запись с id={student_id} уже существует.")

        new_rec: StudentRecord = (
            student_id,
            first_name.strip(),
            second_name.strip(),
            age,
            sex_clean,
        )
        self._students.append(new_rec)
        return new_rec

    def select_record(self,
                      student_id: int | None = None,
                      first_name: str | None = None,
                      second_name: str | None = None,
                      age: int | None = None,
                      sex: str | None = None,
                      ) -> list[StudentRecord]:
        """Получение записей по фильтрам."""
        if all(p is None for p in (student_id, first_name, second_name, age, sex)):
            return self._students.copy()

        result: list[StudentRecord] = []
        for rec in self._students:
            if student_id is not None and rec[0] != student_id:
                continue
            if first_name is not None and rec[1] != first_name:
                continue
            if second_name is not None and rec[2] != second_name:
                continue
            if age is not None and rec[3] != age:
                continue
            if sex is not None and rec[4] != sex:
                continue
            result.append(rec)
        return result

    def update_record(self,
                      student_id: int | None = None,
                      first_name: str | None = None,
                      second_name: str | None = None,
                      age: int | None = None,
                      sex: str | None = None,
                      new_first_name: str | None = None,
                      new_second_name: str | None = None,
                      new_age: int | None = None,
                      new_sex: str | None = None,
                      ) -> list[StudentRecord]:
        """Обновление записей по фильтрам."""
        updated = []

        for i, rec in enumerate(self._students):
            if student_id is not None and rec[0] != student_id:
                continue
            if first_name is not None and rec[1] != first_name:
                continue
            if second_name is not None and rec[2] != second_name:
                continue
            if age is not None and rec[3] != age:
                continue
            if sex is not None and rec[4] != sex:
                continue

            new_rec = (
                rec[0],
                new_first_name if new_first_name is not None else rec[1],
                new_second_name if new_second_name is not None else rec[2],
                new_age if new_age is not None else rec[3],
                new_sex if new_sex is not None else rec[4],
            )
            self._students[i] = new_rec
            updated.append(new_rec)

        if not updated:
            raise RecordNotFoundError("Нет записей, соответствующих фильтру для обновления.")
        return updated

    def delete_record(self,
                      student_id: int | None = None,
                      first_name: str | None = None,
                      second_name: str | None = None,
                      age: int | None = None,
                      sex: str | None = None,
                      ) -> list[StudentRecord] | None:
        """Удаление записей по фильтрам."""
        if all(p is None for p in (student_id, first_name, second_name, age, sex)):
            return None

        deleted = []
        i = 0
        while i < len(self._students):
            rec = self._students[i]
            if student_id is not None and rec[0] != student_id:
                i += 1
                continue
            if first_name is not None and rec[1] != first_name:
                i += 1
                continue
            if second_name is not None and rec[2] != second_name:
                i += 1
                continue
            if age is not None and rec[3] != age:
                i += 1
                continue
            if sex is not None and rec[4] != sex:
                i += 1
                continue

            deleted.append(self._students.pop(i))

        if not deleted:
            raise RecordNotFoundError("Нет записей, соответствующих фильтру для удаления.")
        return deleted

    def sort_records(self, field: str, reverse: bool = False) -> None:
        """Сортировка записей по выбранному полю (возрастание/убывание)."""
        fields = {
            "id": 0,
            "first_name": 1,
            "second_name": 2,
            "age": 3,
            "sex": 4
        }

        if field not in fields:
            raise InvalidDataError(
                f"Неверное поле для сортировки: {field}. "
                f"Доступные поля: {', '.join(fields.keys())}"
            )

        self._students.sort(key=lambda rec: rec[fields[field]], reverse=reverse)
