class AIException(Exception):
    pass

class AINotConfiguredException(AIException):
    pass

class AIAuthException(AIException):
    pass

class AIRateLimitException(AIException):
    pass

class AITimeoutException(AIException):
    pass

class AIProviderException(AIException):
    pass

class AIInvalidRequestException(AIException):
    pass
