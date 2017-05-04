class PolicyError(Exception):
    def __init__(self, message):

        super(PolicyError, self).__init__(message)
