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
