"""
Rate limiting for auth endpoints to prevent brute force.
"""
from rest_framework.throttling import AnonRateThrottle


class AuthRateThrottle(AnonRateThrottle):
    """Stricter rate for login/register (e.g. 10/hour per IP)."""
    scope = 'auth'
