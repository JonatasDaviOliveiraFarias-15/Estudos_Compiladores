class LoxRuntimeError(RuntimeError):
    def __init__(self, message, token=None):
        super().__init__(message)
        self.token = token

class LoxSyntaxError(SyntaxError):
    def __init__(self, message, token=None):
        super().__init__(message)
        self.token = token

class LoxStaticError(Exception):
    def __init__(self, errors):
        super().__init__("Static errors occurred")
        self.errors = errors 