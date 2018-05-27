import os
import os.path
import sys

from ruamel.yaml import YAML


def load_config(path):
    if not os.path.exists(path):
        return {}

    yaml = YAML()
    with open(path, 'r') as fp:
        return yaml.load(fp.read())


def save_config(config, path):
    yaml = YAML()
    yaml.explicit_start = True
    os.makedirs(os.path.dirname(path), mode=0o700, exist_ok=True)
    with os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600), 'w') as fp:
        yaml.dump(config, fp)
