"""
Exception definitions.
"""

class AuthorizationFailure(Exception):
    """
    Return when credentials passed are rejected
    with a 401 response code
    """
    pass

class ResourceNotFound(Exception):
    """
    Return when an object is not found
    """
    pass

class NodeNotInPool(Exception):
    """
    Return when an action for a given node in a pool
    is not in the pool. IE: Drain node X in pool Y
    """
    pass

class ValidationError(Exception):
    """
    Return when PUT/POST returns an error
    """
    pass

class NodeAlreadyExists(Exception):
    """
    Return when a node already exists in a pool
    """
