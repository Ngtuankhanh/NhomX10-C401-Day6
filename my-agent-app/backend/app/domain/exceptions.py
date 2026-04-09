class DomainException(Exception):
    """Base class for all domain exceptions"""
    pass

class FacilityNotFoundError(DomainException):
    def __init__(self, query: str):
        super().__init__(f"No facility found matching query: {query}")

class DoctorNotFoundError(DomainException):
    def __init__(self, query: str):
        super().__init__(f"No doctor found matching query: {query}")
