class StudentDBError(Exception):
    """Базовое исключение для ошибок БД."""
    pass


class RecordNotFoundError(StudentDBError):
    """Запись не найдена."""
    pass


class RecordAlreadyExistsError(StudentDBError):
    """Запись уже существует."""
    pass


class InvalidDataError(StudentDBError):
    """Некорректные данные."""
    pass


class TableNotFoundError(StudentDBError):
    """Таблица не найдена."""
    pass


class TableAlreadyExistsError(StudentDBError):
    """Таблица уже существует."""
    pass


class MissingColumnError(StudentDBError):
    """Отсутствует обязательная колонка."""
    pass


class UnknownColumnError(StudentDBError):
    """Указана неизвестная колонка."""
    pass


class InvalidStorageDataError(StudentDBError):
    """Ошибка чтения/записи данных в файле."""
    pass
