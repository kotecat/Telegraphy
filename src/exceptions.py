class TelegraphyException(Exception):
    pass


class AccountNotFoundException(TelegraphyException):
    pass


class PageNotFoundException(TelegraphyException):
    pass


class PageEditForbiddenException(TelegraphyException):
    pass
