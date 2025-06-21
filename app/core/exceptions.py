class ServiceError(Exception):
    pass


class EntityNotFound(ServiceError):

    def __init__(self, message: str = "Сущность не найдена"):
        super().__init__(message)


class UserNotFoundError(ServiceError):

    def __init__(self, message: str = "Пользователь не найден"):
        super().__init__(message)


class UserAlreadyExistsError(ServiceError):

    def __init__(
        self, message: str = "Пользователь с таким email уже существует"
    ):
        super().__init__(message)


class InvalidCredentialsError(ServiceError):

    def __init__(self, message: str = "Неверные учетные данные"):
        super().__init__(message)
