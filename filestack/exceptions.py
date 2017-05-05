class SecurityError(Exception):
    def __init__(self, message):

        super(SecurityError, self).__init__(message)
