"""
Security Module
Provides CSRF protection, rate limiting, input sanitization, and other security features.
"""

import re
import hashlib
import secrets
import time
from functools import wraps
from typing import Dict, Any, Optional, Callable
from collections import defaultdict
from datetime import datetime, timedelta
import html
import bleach

# Rate limiting storage (use Redis in production)
rate_limit_storage: Dict[str, list] = defaultdict(list)


class CSRFProtection:
    """CSRF token generation and validation"""
    
    def __init__(self, secret_key: str = None):
        self.secret_key = secret_key or secrets.token_hex(32)
        self.tokens: Dict[str, datetime] = {}
        self.token_lifetime = timedelta(hours=1)
    
    def generate_token(self, session_id: str = None) -> str:
        """Generate a new CSRF token"""
        token = secrets.token_urlsafe(32)
        if session_id:
            # Bind token to session
            token_hash = hashlib.sha256(f"{token}{self.secret_key}{session_id}".encode()).hexdigest()
        else:
            token_hash = hashlib.sha256(f"{token}{self.secret_key}".encode()).hexdigest()
        
        self.tokens[token_hash] = datetime.now()
        return token
    
    def validate_token(self, token: str, session_id: str = None) -> bool:
        """Validate a CSRF token"""
        if not token:
            return False
        
        try:
            if session_id:
                token_hash = hashlib.sha256(f"{token}{self.secret_key}{session_id}".encode()).hexdigest()
            else:
                token_hash = hashlib.sha256(f"{token}{self.secret_key}".encode()).hexdigest()
            
            if token_hash in self.tokens:
                # Check token expiration
                if datetime.now() - self.tokens[token_hash] <= self.token_lifetime:
                    # Remove token after use (one-time use)
                    del self.tokens[token_hash]
                    return True
                else:
                    # Token expired, remove it
                    del self.tokens[token_hash]
            
            return False
        except Exception:
            return False
    
    def cleanup_expired_tokens(self):
        """Remove expired tokens"""
        now = datetime.now()
        expired = [token for token, created_at in self.tokens.items() 
                  if now - created_at > self.token_lifetime]
        for token in expired:
            del self.tokens[token]


# Global CSRF protection instance
csrf = CSRFProtection()


def csrf_protect(f: Callable) -> Callable:
    """Decorator to protect endpoints with CSRF validation"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import request, jsonify
        
        # Skip CSRF check for GET, HEAD, OPTIONS
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return f(*args, **kwargs)
        
        # Get token from header or form data
        token = request.headers.get('X-CSRF-Token') or request.form.get('csrf_token')
        session_id = request.cookies.get('session_id')
        
        if not csrf.validate_token(token, session_id):
            return jsonify({'error': 'Invalid or missing CSRF token'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function


class RateLimiter:
    """Rate limiting implementation"""
    
    def __init__(self, requests: int, period: int):
        """
        Initialize rate limiter
        
        Args:
            requests: Number of requests allowed
            period: Time period in seconds
        """
        self.requests = requests
        self.period = period
    
    def is_allowed(self, client_id: str) -> tuple[bool, Optional[int]]:
        """
        Check if request is allowed
        
        Returns:
            (allowed, retry_after_seconds)
        """
        now = time.time()
        
        # Clean old entries
        rate_limit_storage[client_id] = [
            req_time for req_time in rate_limit_storage[client_id]
            if now - req_time < self.period
        ]
        
        # Check if limit exceeded
        if len(rate_limit_storage[client_id]) >= self.requests:
            oldest_request = min(rate_limit_storage[client_id])
            retry_after = int(self.period - (now - oldest_request))
            return False, retry_after
        
        # Add current request
        rate_limit_storage[client_id].append(now)
        return True, None


def rate_limit(requests: int = 100, period: int = 60) -> Callable:
    """
    Decorator for rate limiting
    
    Args:
        requests: Number of requests allowed per period
        period: Time period in seconds (default: 60 seconds)
    """
    limiter = RateLimiter(requests, period)
    
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import request, jsonify
            
            # Use IP address as client identifier
            client_id = request.remote_addr or 'unknown'
            
            # Check rate limit
            allowed, retry_after = limiter.is_allowed(client_id)
            
            if not allowed:
                response = jsonify({
                    'error': 'Rate limit exceeded',
                    'retry_after': retry_after
                })
                response.status_code = 429
                response.headers['Retry-After'] = str(retry_after)
                return response
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator


class InputSanitizer:
    """Input sanitization to prevent XSS, SQL injection, etc."""
    
    # Dangerous patterns
    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
        r"(--|\#|\/\*)",  # SQL comments
        r"(\bOR\b\s+\d+\s*=\s*\d+)",  # OR 1=1
        r"(\bUNION\b.*\bSELECT\b)",  # UNION SELECT
    ]
    
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",  # Event handlers
        r"<iframe",
        r"<object",
        r"<embed",
    ]
    
    PATH_TRAVERSAL_PATTERNS = [
        r"\.\./",
        r"\.\.",
        r"%2e%2e",
        r"%252e%252e",
    ]
    
    COMMAND_INJECTION_PATTERNS = [
        r"[;&|`$]",
        r"\$\(",
        r"\|\|",
        r"&&",
    ]
    
    @staticmethod
    def sanitize_string(value: str, allow_html: bool = False) -> str:
        """
        Sanitize string input
        
        Args:
            value: Input string
            allow_html: If True, allow safe HTML tags
        
        Returns:
            Sanitized string
        """
        if not isinstance(value, str):
            return value
        
        if allow_html:
            # Allow only safe HTML tags
            allowed_tags = ['b', 'i', 'u', 'em', 'strong', 'a', 'p', 'br']
            allowed_attrs = {'a': ['href', 'title']}
            return bleach.clean(value, tags=allowed_tags, attributes=allowed_attrs, strip=True)
        else:
            # Escape all HTML
            return html.escape(value, quote=True)
    
    @classmethod
    def check_sql_injection(cls, value: str) -> bool:
        """Check for SQL injection patterns"""
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        return False
    
    @classmethod
    def check_xss(cls, value: str) -> bool:
        """Check for XSS patterns"""
        for pattern in cls.XSS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        return False
    
    @classmethod
    def check_path_traversal(cls, value: str) -> bool:
        """Check for path traversal patterns"""
        for pattern in cls.PATH_TRAVERSAL_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        return False
    
    @classmethod
    def check_command_injection(cls, value: str) -> bool:
        """Check for command injection patterns"""
        for pattern in cls.COMMAND_INJECTION_PATTERNS:
            if re.search(pattern, value):
                return True
        return False
    
    @classmethod
    def validate_input(cls, value: Any, field_name: str = "input") -> tuple[bool, Optional[str]]:
        """
        Validate input for security issues
        
        Returns:
            (is_valid, error_message)
        """
        if not isinstance(value, str):
            return True, None
        
        if cls.check_sql_injection(value):
            return False, f"{field_name} contains potential SQL injection patterns"
        
        if cls.check_xss(value):
            return False, f"{field_name} contains potential XSS patterns"
        
        if cls.check_path_traversal(value):
            return False, f"{field_name} contains potential path traversal patterns"
        
        if cls.check_command_injection(value):
            return False, f"{field_name} contains potential command injection patterns"
        
        return True, None
    
    @classmethod
    def sanitize_dict(cls, data: Dict[str, Any], allow_html: bool = False) -> Dict[str, Any]:
        """Recursively sanitize dictionary values"""
        result = {}
        for key, value in data.items():
            if isinstance(value, str):
                result[key] = cls.sanitize_string(value, allow_html)
            elif isinstance(value, dict):
                result[key] = cls.sanitize_dict(value, allow_html)
            elif isinstance(value, list):
                result[key] = [
                    cls.sanitize_string(item, allow_html) if isinstance(item, str)
                    else cls.sanitize_dict(item, allow_html) if isinstance(item, dict)
                    else item
                    for item in value
                ]
            else:
                result[key] = value
        return result


def sanitize_input(allow_html: bool = False) -> Callable:
    """Decorator to sanitize request data"""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import request
            
            # Sanitize JSON data
            if request.is_json:
                data = request.get_json()
                if isinstance(data, dict):
                    # Validate inputs
                    for key, value in data.items():
                        is_valid, error = InputSanitizer.validate_input(value, key)
                        if not is_valid:
                            from flask import jsonify
                            return jsonify({'error': error}), 400
            
            # Sanitize form data
            if request.form:
                for key, value in request.form.items():
                    is_valid, error = InputSanitizer.validate_input(value, key)
                    if not is_valid:
                        from flask import jsonify
                        return jsonify({'error': error}), 400
            
            # Sanitize query parameters
            for key, value in request.args.items():
                is_valid, error = InputSanitizer.validate_input(value, key)
                if not is_valid:
                    from flask import jsonify
                    return jsonify({'error': error}), 400
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator


def security_headers(f: Callable) -> Callable:
    """Add security headers to response"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import make_response
        response = make_response(f(*args, **kwargs))
        
        # Content Security Policy
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self';"
        )
        
        # Prevent clickjacking
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        
        # Prevent MIME type sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'
        
        # XSS Protection
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # HSTS (HTTPS only)
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # Referrer Policy
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions Policy
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        return response
    
    return decorated_function


def validate_file_upload(max_size: int = 10_485_760, allowed_extensions: set = None) -> Callable:
    """
    Validate file uploads
    
    Args:
        max_size: Maximum file size in bytes (default: 10MB)
        allowed_extensions: Set of allowed file extensions
    """
    if allowed_extensions is None:
        allowed_extensions = {'xlsx', 'xls', 'csv', 'json'}
    
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import request, jsonify
            
            if 'file' not in request.files:
                return jsonify({'error': 'No file provided'}), 400
            
            file = request.files['file']
            
            if file.filename == '':
                return jsonify({'error': 'Empty filename'}), 400
            
            # Check file extension
            if '.' not in file.filename:
                return jsonify({'error': 'File has no extension'}), 400
            
            ext = file.filename.rsplit('.', 1)[1].lower()
            if ext not in allowed_extensions:
                return jsonify({
                    'error': f'Invalid file type. Allowed: {", ".join(allowed_extensions)}'
                }), 400
            
            # Check file size
            file.seek(0, 2)  # Seek to end
            file_size = file.tell()
            file.seek(0)  # Seek back to start
            
            if file_size > max_size:
                max_mb = max_size / 1_048_576
                return jsonify({
                    'error': f'File too large. Maximum size: {max_mb}MB'
                }), 400
            
            # Check for path traversal in filename
            if InputSanitizer.check_path_traversal(file.filename):
                return jsonify({'error': 'Invalid filename'}), 400
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator


# Utility functions

def generate_secure_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token"""
    return secrets.token_urlsafe(length)


def hash_password(password: str, salt: str = None) -> tuple[str, str]:
    """
    Hash a password with salt
    
    Returns:
        (hashed_password, salt)
    """
    if salt is None:
        salt = secrets.token_hex(16)
    
    hashed = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode(),
        salt.encode(),
        100000  # iterations
    )
    
    return hashed.hex(), salt


def verify_password(password: str, hashed: str, salt: str) -> bool:
    """Verify a password against its hash"""
    new_hash, _ = hash_password(password, salt)
    return secrets.compare_digest(new_hash, hashed)


# Example usage and testing
if __name__ == "__main__":
    # Test CSRF protection
    print("Testing CSRF Protection...")
    token = csrf.generate_token("session123")
    print(f"Generated token: {token}")
    print(f"Valid token: {csrf.validate_token(token, 'session123')}")
    print(f"Invalid token: {csrf.validate_token('invalid', 'session123')}")
    
    # Test input sanitization
    print("\nTesting Input Sanitization...")
    test_inputs = [
        "Normal text",
        "<script>alert('XSS')</script>",
        "SELECT * FROM users WHERE id=1",
        "../../../etc/passwd",
        "test; rm -rf /",
    ]
    
    for test_input in test_inputs:
        is_valid, error = InputSanitizer.validate_input(test_input)
        print(f"Input: {test_input[:50]}")
        print(f"Valid: {is_valid}, Error: {error}")
        print()
    
    # Test rate limiting
    print("\nTesting Rate Limiting...")
    limiter = RateLimiter(requests=5, period=10)
    
    for i in range(7):
        allowed, retry_after = limiter.is_allowed("client1")
        print(f"Request {i+1}: Allowed={allowed}, RetryAfter={retry_after}")
