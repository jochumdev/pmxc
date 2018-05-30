import os
import os.path
import sys
import json


def load_config(path):
    if not os.path.exists(path):
        return {}

    with open(path, 'r') as fp:
        content = fp.read()
        return json.loads(content)


def save_config(config, path):
    os.makedirs(os.path.dirname(path), mode=0o700, exist_ok=True)
    with os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600), 'w') as fp:
        content =  json.dumps(config, indent=4, sort_keys=True)
        fp.write(content)
