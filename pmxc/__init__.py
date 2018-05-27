import os
import os.path

__all__ = [
    "__version__",
    "DEFAULT_CONFIG_FILE",
]

__version__ = "5.2.0.0"
DEFAULT_CONFIG_FILE = os.getenv('PMXC_CONFIG', os.path.join(os.path.expanduser("~"), ".config", "pmxc", 'config.yaml'))