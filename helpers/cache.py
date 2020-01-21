import json
import os

cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "caches")
if not os.path.exists(cache_dir):
    os.mkdir(cache_dir)

caches = {}


def cache_path(name):
    return os.path.join(cache_dir, name + ".json")


def clear_cache(name, *parents):
    if name in parents:
        return

    path = cache_path(name)
    if os.path.exists(path):
        os.remove(path)

    for dependency in caches[name]:
        clear_cache(dependency, name, *parents)


def cache(name, dependencies=None, refresh=False):
    if dependencies is None:
        dependencies = []
    if name in caches:
        raise RuntimeError(f"Cache {name} is already registered")

    caches[name] = dependencies
    if "/" not in name:
        path = cache_path(name)
    else:
        path = name + ".json"

    def decorator(function):
        def wrapper(*args, **kwargs):
            if refresh:
                clear_cache(name)
            if os.path.exists(path):
                with open(path, "r") as f:
                    return json.load(f)
            res = function(*args, **kwargs)
            with open(path, "w") as f:
                json.dump(res, f, indent=2)
            return res

        return wrapper

    return decorator
