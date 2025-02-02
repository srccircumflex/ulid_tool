"""
Monotone counters for the random part of a ULID.

- runtime counter: starts at 0 with every runtime (not thread save)
- local counter: reads the last status from a local file (not thread save)
- env counter: reads the last env id from a local file and uses the last 8 bits of the random part for this id, the rest is set analogous to the runtime counter (thread save)

All counters count monotonically up to the highest possible value and then reset to 0.
"""

from pathlib import Path
import atexit
from time import sleep
from warnings import warn

LOCAL_FILE = Path(__file__).parent / ".lexical_rand.cache"
MAX_RAND = 1208925819614629174706175

ENV_LOCK_FILE = Path(__file__).parent / ".lexical_env.lock"
ENV_FILE = Path(__file__).parent / ".lexical_env.cache"
MAX_ENV = 255
MAX_ENV_RAND = 4722366482869645213695


def __env_gen():
    for _ in range(100):
        if not ENV_LOCK_FILE.exists():
            break
        else:
            sleep(.001)
    else:
        warn(f"\n"
             f"Timeout: {ENV_LOCK_FILE=} not released in 0.1s\n"
             f"-> continuation in force mode")
    with open(ENV_LOCK_FILE, "w"):
        try:
            with open(ENV_FILE, "r+") as f:
                env_id = int(f.read()) + 1
                if env_id > MAX_ENV:
                    env_id = 0
                f.seek(0)
                f.write(str(env_id))
                f.truncate()
        except FileNotFoundError:
            env_id = 0
            with open(ENV_FILE, "w") as f:
                f.write("0")
    ENV_LOCK_FILE.unlink()
    while True:
        for i in range(MAX_ENV_RAND + 1):
            yield (i << 8) | env_id


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
__env_gen__ = __env_gen()


def runtime_next() -> int:
    return next(__runtime_gen__)


def local_next() -> int:
    return next(__local_gen__)


def env_next() -> int:
    return next(__env_gen__)

