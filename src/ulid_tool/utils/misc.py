from time import time_ns


def time_ms() -> int: return time_ns() // 1_000_000


try:
    from os import urandom as _ranb_
    if _ranb_(1) == _ranb_(1) and _ranb_(1) == _ranb_(1):
        raise SystemError
except (ImportError, SystemError):
    from random import randbytes as _ranb_


def _randb(n: int) -> bytes:
    """[ ! ] Do not use before validation"""
    return _ranb_(n)
