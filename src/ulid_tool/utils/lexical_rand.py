"""
Monotone counters for the random part of a ULID.

The runtime counter starts at 0 with every runtime.
The local counter reads the last status from a file.
Both counters count monotonically up to the highest possible value and then reset to 0.
"""

from pathlib import Path
import atexit

LOCAL_FILE = Path(__file__).parent / ".lexical_rand.cache"
MAX_RAND = 1208925819614629174706175


def __runtime_gen():
    while True:
        for i in range(MAX_RAND + 1):
            yield i


def __local_gen():
    try:
        with open(LOCAL_FILE) as f:
            li = i = int(f.read())
    except Exception:
        li = i = 0

    def _atexit_():
        with open(LOCAL_FILE, "w") as f:
            f.write(str(li))

    atexit.register(_atexit_)

    for i in range(i + 1, MAX_RAND + 1):
        li = i
        yield i

    while True:
        for i in range(MAX_RAND + 1):
            li = i
            yield i


__runtime_gen__ = __runtime_gen()
__local_gen__ = __local_gen()


def runtime_next() -> int:
    return next(__runtime_gen__)


def local_next() -> int:
    return next(__local_gen__)

