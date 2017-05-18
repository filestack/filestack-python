class SecurityError(Exception):
    def __init__(self, message):

        super(SecurityError, self).__init__(message)


class FilestackException(Exception):
    def __init__(self, message):

        super(FilestackException, self).__init__(message)
