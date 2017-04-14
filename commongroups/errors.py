# coding: utf-8

"""
Special errors for commongroups.
"""


class CommonError(Exception):
    """Base Exception for all commongroups errors."""
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)


class MissingParamError(CommonError):
    """Raised upon failure to access a configuration or group parameter."""
    def __init__(self, param, *args, **kwargs):
        self.param = param
        super().__init__(self, *args, **kwargs)

    def __str__(self):
        msg = 'Missing parameter: {0}'.format(self.param)
        return msg


class NoCredentialsError(CommonError):
    """Raised when the Google API credentials file cannot be read."""
    def __init__(self, path, *args, **kwargs):
        self.path = path
        super().__init__(self, *args, **kwargs)

    def __str__(self):
        msg = 'Cannot read Google API credentials key file: {0}'
        return msg.format(self.path)
