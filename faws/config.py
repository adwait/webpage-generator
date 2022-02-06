import collections

Config = collections.namedtuple(
    "Config", ["verbosity", "prefix", "target", "templates"]
)
