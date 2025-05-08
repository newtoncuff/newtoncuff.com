from datetime import datetime, timedelta
from flask import current_app
from . import get_redis

import json

"""<-----Class Docstring
RedisCache is a utility class for interacting with a Redis cache. It provides static methods
to set, get, and delete cache entries. The class assumes the presence of a `get_redis` function
to obtain a Redis client and uses JSON serialization for non-string values.
Methods:
    set(key, value, expire=3600):
        Stores a value in the Redis cache with a specified expiration time (default is 3600 seconds).
        Automatically serializes non-string values to JSON.
    get(key, default=None):
        Retrieves a value from the Redis cache. If the value is JSON-encoded, it will be deserialized.
        Returns the default value if the key does not exist or an error occurs.
    delete(key):
        Deletes a key from the Redis cache. Returns True if the key was successfully deleted, False otherwise.
"""
class RedisCache:
    
    """<-----Method Docstring
    Set a value in the Redis cache with an optional expiration time.
    Args:
        key (str): The key under which the value will be stored in the cache.
        value (Any): The value to store in the cache. If not a string, it will be serialized to JSON.
        expire (int, optional): The expiration time for the cache entry in seconds. Defaults to 3600 seconds (1 hour).
    Returns:
        bool: True if the value was successfully set in the cache, False otherwise.
    Notes:
        - This function requires a valid Redis client connection. If the client is not available, it will return False.
        - Any exceptions during the operation are logged and the function will return False.
    """
    @staticmethod
    def set(key, value, expire=3600):        
        
        client = get_redis()
        if not client:
            return False
            
        try:
            # Convert value to JSON if it's not a string
            if not isinstance(value, str):
                value = json.dumps(value)
                
            return client.setex(key, expire, value)
        except Exception as e:
            current_app.logger.error(f"Redis cache set error: {str(e)}")
            return False
    
    """<-----Method Docstring
    Retrieve a value from the Redis cache by its key.
    Args:
        key (str): The key to look up in the Redis cache.
        default (Any, optional): The default value to return if the key is not found 
            or if there is an issue with the Redis client. Defaults to None.
    Returns:
        Any: The value associated with the key in the Redis cache. If the value is 
            JSON-encoded, it will be decoded and returned as a Python object. If the 
            value is not JSON-encoded, it will be returned as a string. If the key 
            is not found or an error occurs, the default value is returned.
    """
    @staticmethod
    def get(key, default=None):        
        
        client = get_redis()
        if not client:
            return default
            
        try:
            value = client.get(key)
            if value is None:
                return default
                
            # Try to decode JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                # Return as string if not JSON
                return value.decode('utf-8') if isinstance(value, bytes) else value
        except Exception as e:
            current_app.logger.error(f"Redis cache get error: {str(e)}")
            return default
    
    """<-----Method Docstring
    Deletes a key from the Redis cache.
    Args:
        key (str): The key to be deleted from the Redis cache.
    Returns:
        bool: True if the key was successfully deleted, False otherwise.
    Notes:
        - If the Redis client is not available, the function returns False.
        - Logs an error message if an exception occurs during the deletion process.
    """
    @staticmethod
    def delete(key):        

        client = get_redis()
        if not client:
            return False
            
        try:
            return client.delete(key) > 0
        except Exception as e:
            current_app.logger.error(f"Redis cache delete error: {str(e)}")
            return False
    
