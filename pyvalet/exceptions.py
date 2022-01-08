class SeriesException(BaseException):
    """Raised when there is a problem locating the provided series."""
    pass


class GroupException(BaseException):
    """Raised when there is a problem locating the provided group."""
    pass

class BOCException(BaseException):
    """Raised when there is a problem with Bank of Canada connection or data."""
    pass
