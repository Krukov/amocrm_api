class BaseModuleException(Exception):
    """
    Base exception for all
    """


class AmoApiException(BaseModuleException):
    """
    Base exception for errors from the amocrm api side
    """


class UnAuthorizedException(AmoApiException):
    """
    Something wrong with access token or credations
    """


class PermissionsDenyException(AmoApiException):
    """
    No permissions
    """


class NotFound(AmoApiException):
    """
    Amocrm api return 404 or nothing
    """


class NoToken(BaseModuleException):
    """
    Raised if there are no access token in the storage
    Action - init token
    """


class NoDataException(BaseModuleException):
    """
    Exception raised when no data found for field
    Wrong mapping or field may be blank (blank=True)
    """


class ValidationError(BaseModuleException):
    """
    Exception for validation error response from amocrm
    """


class InitException(BaseModuleException):
    """
    Instance have no id, create instance first
    """
