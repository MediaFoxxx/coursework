from functools import wraps
from coursework.cache.connection import RedisCache


def fetch_from_cache(cache_name, cache_config):
    cache_conn = RedisCache(cache_config['redis'])
    ttl = cache_config['ttl']

    def wrapper_func(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            cache_value = cache_conn.get_value(cache_name)
            print('cashed_value=', cache_value)
            if cache_value:
                return cache_value
            response = f(*args, **kwargs)
            print('response=', response)
            cache_conn.set_value(cache_name, response, ttl=ttl)
            return response
        return wrapper
    return wrapper_func
