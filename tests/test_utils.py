# tests/test_utils.py
import time
import random
import os
from functools import wraps

def retry_on_503(max_retries=None, delay=None, backoff=None):
    """Decorator to retry tests on 503 Service Unavailable errors"""
    # Use environment variables for configuration if not provided
    max_retries = max_retries or int(os.getenv("TEST_RETRY_MAX_ATTEMPTS", "3"))
    delay = delay or float(os.getenv("TEST_RETRY_DELAY", "1"))
    backoff = backoff or float(os.getenv("TEST_RETRY_BACKOFF", "2"))
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    # Check if it's a 503 error or related service unavailable errors
                    error_str = str(e).lower()
                    if any(term in error_str for term in ["503", "service unavailable", "temporarily unavailable", "server error"]):
                        if attempt < max_retries:
                            # Calculate delay with jitter to avoid thundering herd
                            wait_time = delay * (backoff ** attempt) + random.uniform(0, 1)
                            print(f"503/Service Unavailable error on attempt {attempt + 1}, retrying in {wait_time:.2f}s...")
                            time.sleep(wait_time)
                            continue
                    
                    # If it's not a 503 or we've exhausted retries, re-raise
                    raise e
            
            # This should never be reached, but just in case
            raise last_exception
        return wrapper
    return decorator

def retry_on_network_error(max_retries=None, delay=None, backoff=None):
    """Decorator to retry tests on network-related errors"""
    # Use environment variables for configuration if not provided
    max_retries = max_retries or int(os.getenv("TEST_RETRY_MAX_ATTEMPTS", "3"))
    delay = delay or float(os.getenv("TEST_RETRY_DELAY", "1"))
    backoff = backoff or float(os.getenv("TEST_RETRY_BACKOFF", "2"))
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    # Check if it's a network-related error
                    error_str = str(e).lower()
                    if any(term in error_str for term in [
                        "503", "service unavailable", "temporarily unavailable", 
                        "timeout", "connection", "network", "temporary failure",
                        "502", "504", "bad gateway", "gateway timeout"
                    ]):
                        if attempt < max_retries:
                            # Calculate delay with jitter to avoid thundering herd
                            wait_time = delay * (backoff ** attempt) + random.uniform(0, 1)
                            print(f"Network error on attempt {attempt + 1}, retrying in {wait_time:.2f}s...")
                            time.sleep(wait_time)
                            continue
                    
                    # If it's not a network error or we've exhausted retries, re-raise
                    raise e
            
            # This should never be reached, but just in case
            raise last_exception
        return wrapper
    return decorator
