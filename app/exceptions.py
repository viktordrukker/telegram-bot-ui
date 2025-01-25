class InvalidStateError(Exception):
    """Raised when attempting an invalid state transition"""
    def __init__(self, message: str):
        super().__init__(message)
        self.code = 409  # Conflict HTTP status code