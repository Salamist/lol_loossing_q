import json, atexit
import functools
import logging

# file_name = 'cache.json'

def persist_to_file(file_name):

    try:
        cache = json.load(open(file_name, 'r'))
    except (IOError, ValueError):
        cache = {}

    def _save_cache():
        with open(file_name, 'w') as f:
            json.dump(cache, f, indent=2, sort_keys=True)

    # atexit.register(lambda: json.dump(cache, open(file_name, 'w'), indent=2, sort_keys=True))
    atexit.register(_save_cache)

    def func_wrapper(func):
        @functools.wraps(func)
        def new_func(*args, **kwargs):
            _, param = args
            if param not in cache:
                cache[param] = func(*args, **kwargs)
            return cache[param]
        return new_func
    return func_wrapper
