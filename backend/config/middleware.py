"""
Security headers middleware — adds high-security HTTP response headers.
"""
import logging

logger = logging.getLogger('security')


class SecurityHeadersMiddleware:
    """
    Add security-related response headers:
    - Referrer-Policy: strict-origin-when-cross-origin
    - Permissions-Policy: restrict sensitive features
    - X-Content-Type-Options is set by SecurityMiddleware; we reinforce minimal set.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = (
            'accelerometer=(), camera=(), geolocation=(), gyroscope=(), '
            'magnetometer=(), microphone=(), payment=(), usb=()'
        )
        return response
