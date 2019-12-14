class SeriesException(BaseException):
    """Raised when there is a problem locating the provided series."""
    pass


class GroupException(BaseException):
    """Raised when there is a problem locating the provided group."""
    pass


class RequestException(BaseException):
    """Raised  when there is some unexpected problem with a request"""