class PublishingError(Exception):
    def __init__(self, message: str, code: str = "UNKNOWN_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)

class AuthenticationError(PublishingError):
    def __init__(self, message: str):
        super().__init__(message, "AUTHENTICATION_ERROR")

class AuthorizationError(PublishingError):
    def __init__(self, message: str):
        super().__init__(message, "AUTHORIZATION_ERROR")

class RateLimitError(PublishingError):
    def __init__(self, message: str):
        super().__init__(message, "RATE_LIMITED")

class InvalidContentError(PublishingError):
    def __init__(self, message: str):
        super().__init__(message, "INVALID_CONTENT")

class UnsupportedContentError(PublishingError):
    def __init__(self, message: str):
        super().__init__(message, "UNSUPPORTED_CONTENT")

class NetworkError(PublishingError):
    def __init__(self, message: str):
        super().__init__(message, "NETWORK_ERROR")

class ProviderError(PublishingError):
    def __init__(self, message: str):
        super().__init__(message, "PROVIDER_ERROR")

class NotConfiguredError(PublishingError):
    def __init__(self, message: str = "Provider is not configured or missing credentials."):
        super().__init__(message, "NOT_CONFIGURED")
