from flask import current_app

import sys
import importlib
import redis

"""<-----Class Docstring
RedisService is a singleton class that provides a centralized interface for managing
a Redis client connection. It ensures that only one instance of the Redis client
is created and reused throughout the application.
The class supports lazy initialization of the Redis client, allowing it to connect
to a Redis server based on the application's configuration. It handles both modern
and legacy versions of the `redis` Python package and provides robust error handling
and logging during the connection process.
Attributes:
    _instance (RedisService): The singleton instance of the RedisService class.
    _client (redis.client.Redis or redis.client.StrictRedis): The Redis client instance.
Methods:
    get_instance():
        Retrieves the singleton instance of the RedisService class.
    client:
        Lazily initializes and returns the Redis client instance, connecting to
        the Redis server based on the application's configuration.
"""
class RedisService:    
    
    # Class-level properties
    _instance = None
    _client = None
    #end of class-level properties
    
    """<-----Method Docstring
    Retrieve the singleton instance of the class. If the instance does not 
    already exist, create it and store it as a class-level attribute.
    Returns:
        object: The singleton instance of the class.
    """  
    @classmethod
    def get_instance(cls):      
        
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    

    """<-----Method Docstring
    Lazily initializes and returns a Redis client instance.
    This method attempts to create a Redis client using the configuration
    provided in the Flask application's `REDIS_URL` setting. If `REDIS_URL`
    is not set and the environment is not production, it defaults to
    `redis://localhost:6379/0`. In a production environment, the absence of
    `REDIS_URL` raises a `ValueError`.
    The method supports both modern `Redis` (>=4.x) and legacy `StrictRedis`
    classes from the `redis` Python package. It parses the Redis URL manually
    to extract the host, port, and database index.
    If the Redis client is successfully created, it attempts to test the
    connection by sending a `PING` command. Any errors during the initialization
    or connection process are logged.
    Returns:
        redis.client.Redis or redis.client.StrictRedis: A Redis client instance
        if the connection is successful, or `None` if the initialization fails.
    Raises:
        ValueError: If `REDIS_URL` is not set in a production environment.
    """
    @property
    def client(self):        

        if self._client is None:
            try:
                redis_url = current_app.config.get('REDIS_URL')
                if not redis_url:
                    if current_app.config.get('ENV') == 'production':
                        raise ValueError("REDIS_URL must be set in production environment")
                    else:
                        redis_url = 'redis://localhost:6379/0'
                        current_app.logger.warning("REDIS_URL not set, defaulting to localhost for development")

                current_app.logger.info(f"Connecting to Redis using URL: {redis_url}")
                
                # Try importing directly
                try:
                    # For modern redis-py package (>=4.x)
                    from redis import Redis
                    
                    # Parse URL manually
                    if redis_url.startswith('redis://'):
                        parts = redis_url.replace('redis://', '').split(':')
                        host = parts[0] or 'localhost'
                        
                        if len(parts) > 1:
                            port_db = parts[1].split('/')
                            port = int(port_db[0]) if port_db[0] else 6379
                            db = int(port_db[1]) if len(port_db) > 1 and port_db[1] else 0
                        else:
                            port = 6379
                            db = 0
                        
                        current_app.logger.info(f"Connecting to Redis at {host}:{port}/{db}")
                        self._client = Redis(host=host, port=port, db=db)
                    else:
                        current_app.logger.warning("Invalid Redis URL format, using defaults")
                        self._client = Redis(host='localhost', port=port, db=db)
                    
                    current_app.logger.info("Created Redis client using Redis class")
                except (ImportError, AttributeError) as e:
                    current_app.logger.error(f"Redis class import failed: {str(e)}")
                    
                    # Try StrictRedis for older versions
                    try:
                        from redis import StrictRedis
                        parts = redis_url.replace('redis://', '').split(':')
                        host = parts[0] or 'localhost'
                        
                        if len(parts) > 1:
                            port_db = parts[1].split('/')
                            port = int(port_db[0]) if port_db[0] else 6379
                            db = int(port_db[1]) if len(port_db) > 1 and port_db[1] else 0
                        else:
                            port = 6379
                            db = 0
                        
                        current_app.logger.info(f"Connecting to Redis with StrictRedis at {host}:{port}/{db}")
                        self._client = StrictRedis(host=host, port=port, db=db)
                        current_app.logger.info("Created Redis client using StrictRedis class")
                    except (ImportError, AttributeError) as e:
                        current_app.logger.error(f"StrictRedis import failed: {str(e)}")
                
                # Test connection
                if self._client:
                    self._client.ping()
                    current_app.logger.info("Redis connected successfully!")
                else:
                    current_app.logger.error("Failed to create Redis client")
            except Exception as e:
                current_app.logger.error(f"Redis connection error: {str(e)}")
                self._client = None
        return self._client


"""<-----Method Docstring
Initializes the Redis service for the given application.
This function sets up the Redis service, defines a getter for the Redis client,
and imports necessary components for caching functionality. It returns a dictionary
containing the initialized Redis service, the getter function, and the imported components.
Args:
    app: The application instance to associate with the Redis service.
Returns:
    dict: A dictionary containing the following keys:
        - 'redis_service': The initialized RedisService instance.
        - 'get_redis': A lambda function to retrieve the Redis client.
        - 'RedisCache': The RedisCache class for caching operations.
        - 'cached': The cached decorator for caching function results.
"""
def init_redis(app):
    
    global redis_service, get_redis, RedisCache, cached
    
    # Create service
    redis_service = RedisService.get_instance()
    
    # Define getter
    get_redis = lambda: redis_service.client
    
    # Import components
    from .Service import RedisCache
    from .decorators import cached
    
    return {
        'redis_service': redis_service,
        'get_redis': get_redis,
        'RedisCache': RedisCache,
        'cached': cached
    }