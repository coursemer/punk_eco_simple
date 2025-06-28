"""
Configuration for JWT (JSON Web Tokens) used in the application.
"""

import os
from datetime import timedelta

class JWTConfig:
    """Configuration class for JWT."""
    
    # Secret key for signing tokens - should be kept secret in production
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-this-in-production')
    
    # Token expiration times
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)  # Access token expires in 1 hour
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)  # Refresh token expires in 30 days
    
    # Token location (headers, cookies, etc.)
    JWT_TOKEN_LOCATION = ['headers']
    
    # Header name for JWT tokens
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    
    # CSRF protection for cookies (if using cookies)
    JWT_COOKIE_SECURE = False  # Set to True in production with HTTPS
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_CSRF_IN_COOKIES = True
    
    # Blacklist configuration
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    
    # Error messages
    JWT_ERROR_MESSAGE_KEY = 'error'
    
    # Custom claims
    JWT_IDENTITY_CLAIM = 'identity'  # Default is 'identity'
    JWT_USER_CLAIMS = 'user_claims'  # Default is 'user_claims'
