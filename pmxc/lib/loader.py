import importlib
import pkgutil


__all__ = [
    "load_all",
]

def load_all(package):
    """
    https://stackoverflow.com/a/1707786/3368468
    """
    result = {}
    for _, modname, _ in pkgutil.iter_modules(package.__path__):
        module = importlib.import_module(
            package.__name__ + '.' + modname, package)
        result[modname] = module
    return result
