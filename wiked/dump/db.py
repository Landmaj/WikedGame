import dbm.gnu
from pathlib import Path

import msgpack


class DB:
    def __init__(self, path: Path, mode: str):
        self.db = dbm.gnu.open(path.as_posix(), mode)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()

    def __getitem__(self, key):
        if not isinstance(key, bytes):
            key: bytes = msgpack.packb(key, use_bin_type=True)
        return msgpack.unpackb(self.db[key], use_list=True, raw=False)

    def __setitem__(self, key, value):
        key: bytes = msgpack.packb(key, use_bin_type=True)
        value: bytes = msgpack.packb(value, use_bin_type=True)
        self.db[key] = value

    def keys(self):
        return self.db.keys()
