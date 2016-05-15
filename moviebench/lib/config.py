import yaml

CONFIG = yaml.load('config/base.yaml')


def get(key, default=None):
    d = CONFIG
    for k in key.split('.'):
        d = d.get(k)
    if d is None:
        return default
    return d
