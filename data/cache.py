# data/cache.py
import os
import json
import time
import logging
from datetime import datetime, timedelta
import pandas as pd

logger = logging.getLogger(__name__)

class DataCache:
    """
    Cache for API responses to reduce redundant calls.
    Stores responses with TTL (time to live).
    """
    def __init__(self, cache_dir='./cache', ttl_seconds=300):
        """
        Initialize cache with directory and TTL.
        
        Parameters:
            cache_dir (str): Directory to store cache files
            ttl_seconds (int): Time to live in seconds
        """
        self.cache_dir = cache_dir
        self.ttl_seconds = ttl_seconds
        
        # Create cache directory if it doesn't exist
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        
        logger.info(f"Initialized DataCache at {cache_dir} with TTL={ttl_seconds}s")
    
    def _get_cache_path(self, key):
        """Get path for cache file given a key."""
        # Create valid filename from key
        valid_filename = "".join(c if c.isalnum() else "_" for c in key)
        return os.path.join(self.cache_dir, f"{valid_filename}.json")
    
    def get(self, key):
        """
        Get value from cache if it exists and is not expired.
        
        Parameters:
            key (str): Cache key
            
        Returns:
            any: Cached value or None if not found or expired
        """
        cache_path = self._get_cache_path(key)
        
        if not os.path.exists(cache_path):
            return None
        
        try:
            with open(cache_path, 'r') as f:
                cache_data = json.load(f)
            
            # Check if cache has expired
            timestamp = cache_data.get('timestamp', 0)
            if time.time() - timestamp > self.ttl_seconds:
                logger.debug(f"Cache expired for key: {key}")
                return None
            
            logger.debug(f"Cache hit for key: {key}")
            return cache_data.get('value')
        
        except Exception as e:
            logger.warning(f"Error reading cache for key {key}: {str(e)}")
            return None
    
    def set(self, key, value):
        """
        Store value in cache with current timestamp.
        
        Parameters:
            key (str): Cache key
            value (any): Value to cache (must be JSON serializable)
        """
        cache_path = self._get_cache_path(key)
        
        try:
            cache_data = {
                'timestamp': time.time(),
                'value': value
            }
            
            with open(cache_path, 'w') as f:
                json.dump(cache_data, f)
            
            logger.debug(f"Cached value for key: {key}")
            return True
        
        except Exception as e:
            logger.warning(f"Error writing cache for key {key}: {str(e)}")
            return False
    
    def clear(self, key=None):
        """
        Clear specific cache entry or all cache if key is None.
        
        Parameters:
            key (str, optional): Cache key to clear, or None to clear all
            
        Returns:
            bool: Success status
        """
        if key:
            # Clear specific entry
            cache_path = self._get_cache_path(key)
            if os.path.exists(cache_path):
                try:
                    os.remove(cache_path)
                    logger.debug(f"Cleared cache for key: {key}")
                    return True
                except Exception as e:
                    logger.warning(f"Error clearing cache for key {key}: {str(e)}")
                    return False
            return True
        else:
            # Clear all cache
            try:
                for filename in os.listdir(self.cache_dir):
                    file_path = os.path.join(self.cache_dir, filename)
                    if os.path.isfile(file_path) and filename.endswith('.json'):
                        os.remove(file_path)
                logger.info("Cleared all cache entries")
                return True
            except Exception as e:
                logger.warning(f"Error clearing all cache: {str(e)}")
                return False
    
    def cleanup_expired(self):
        """
        Remove all expired cache entries.
        
        Returns:
            int: Number of entries removed
        """
        count = 0
        try:
            for filename in os.listdir(self.cache_dir):
                file_path = os.path.join(self.cache_dir, filename)
                if os.path.isfile(file_path) and filename.endswith('.json'):
                    try:
                        with open(file_path, 'r') as f:
                            cache_data = json.load(f)
                        
                        # Check if cache has expired
                        timestamp = cache_data.get('timestamp', 0)
                        if time.time() - timestamp > self.ttl_seconds:
                            os.remove(file_path)
                            count += 1
                    except Exception:
                        # If file is corrupted, remove it
                        os.remove(file_path)
                        count += 1
            
            logger.info(f"Removed {count} expired cache entries")
            return count
        
        except Exception as e:
            logger.warning(f"Error cleaning up expired cache: {str(e)}")
            return 0

# Initialize global cache
cache = DataCache()

def cached_api_call(func):
    """
    Decorator for caching API calls.
    
    Parameters:
        func: Function to decorate
        
    Returns:
        Wrapped function that uses cache
    """
    def wrapper(*args, **kwargs):
        # Create cache key from function name and arguments
        key = f"{func.__name__}_{str(args)}_{str(kwargs)}"
        
        # Try to get from cache
        cached_result = cache.get(key)
        if cached_result is not None:
            return cached_result
        
        # Not in cache, call function
        result = func(*args, **kwargs)
        
        # Store in cache
        cache.set(key, result)
        
        return result
    
    return wrapper