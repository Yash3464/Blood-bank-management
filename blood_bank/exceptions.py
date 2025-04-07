"""
Custom exceptions for the Blood Bank Management System.
These exceptions help in better error handling and provide more specific error messages.
"""

class BloodBankError(Exception):
    """Base exception class for Blood Bank Management System"""
    pass

class DonorNotFoundError(BloodBankError):
    """Raised when a donor is not found in the system"""
    pass

class InsufficientBloodUnitsError(BloodBankError):
    """Raised when there are insufficient blood units available"""
    pass

class BloodRequestError(BloodBankError):
    """Raised when there's an error processing a blood request"""
    pass

class InvalidBloodGroupError(BloodBankError):
    """Raised when an invalid blood group is provided"""
    pass

class DonationError(BloodBankError):
    """Raised when there's an error processing a blood donation"""
    pass 