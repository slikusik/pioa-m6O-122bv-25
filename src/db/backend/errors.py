class StudentDBError(Exception):
    pass

class RecordNotFoundError(StudentDBError):
    pass

class RecordAlreadyExistsError(StudentDBError):
    pass

class InvalidDataError(StudentDBError):
    pass

class TableNotFoundError(StudentDBError):
    pass

class TableAlreadyExistsError(StudentDBError):
    pass

class MissingColumnError(StudentDBError):
    pass

class UnknownColumnError(StudentDBError):
    pass

class InvalidStorageDataError(StudentDBError):
    pass
