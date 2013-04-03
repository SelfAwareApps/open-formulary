"""
Exceptions for open formulary
"""
class Error(Exception):
    """
    Base error class for our exceptions to inherit from
    """

class ValidationError(Error):
    """
    Some kind of validation error with a form submission
    """
