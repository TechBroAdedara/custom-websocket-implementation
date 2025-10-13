class MyAppException(Exception):
    pass


class UserServiceException(MyAppException):
    pass


class InvalidAPIKey(MyAppException):
    pass


class InvalidTokenError(MyAppException):
    pass


class UnauthorizedWebsocket(MyAppException):
    pass


class InvalidWebsocketMessage(MyAppException):
    pass

class InvalidWebsocketAction(MyAppException):
    pass

class NonExistentWebsocketRecipient(MyAppException):
    pass
