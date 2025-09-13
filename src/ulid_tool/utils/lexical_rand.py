"""
Monotone counters for the random part of a ULID.

- runtime counter: starts at 0 with every runtime (not thread save)
- local counter: reads the last status from a local file (not thread save)
- env counter: reads the last env id from a local file and uses the last 8 bits of the random part for this id, the rest is set analogous to the runtime counter (thread save)

All counters count monotonically up to the highest possible value and then reset to 0.
"""
import atexit
import threading
from pathlib import Path

import filelock

LOCAL_FILE = Path(__file__).parent / ".lexical_rand.cache"
MAX_RAND = 1208925819614629174706175

ENV_LOCK_FILE = Path(__file__).parent / ".env-lock"

ENV_FILE = Path(__file__).parent / ".lexical_env.cache"
T_ENV_FILE = Path(__file__).parent / ".thread_env.cache"

MAX_ENV = 255
MAX_ENV_RAND = 4722366482869645213695

S_ENV_FILE = Path(__file__).parent / ".short_env.cache"
MAX_S_ENV = 15
MAX_S_ENV_RAND = 15


__lock__ = filelock.FileLock(ENV_LOCK_FILE)


def __env_gen():
    # [COUNTER(72bit)][ENV-ID(8bit)]
    with __lock__:
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
    while True:
        for i in range(MAX_ENV_RAND + 1):
            yield (i << 8) | env_id


def __t_env_gen():
    # [COUNTER(72bit)][ENV-ID(8bit)]
    with __lock__:
        try:
            with open(T_ENV_FILE, "r+") as f:
                env_id = int(f.read()) + 1
                if env_id > MAX_ENV:
                    env_id = 0
                f.seek(0)
                f.write(str(env_id))
                f.truncate()
        except FileNotFoundError:
            env_id = 0
            with open(T_ENV_FILE, "w") as f:
                f.write("0")
    while True:
        for i in range(MAX_ENV_RAND + 1):
            yield (i << 8) | env_id


def __s_env_gen():
    # [COUNTER(4bit)][ENV-ID(4bit)]
    with __lock__:
        try:
            with open(S_ENV_FILE, "r+") as f:
                s_env_id = int(f.read()) + 1
                if s_env_id > MAX_S_ENV:
                    s_env_id = 0
                f.seek(0)
                f.write(str(s_env_id))
                f.truncate()
        except FileNotFoundError:
            s_env_id = 0
            with open(S_ENV_FILE, "w") as f:
                f.write("0")
    while True:
        for i in range(MAX_S_ENV_RAND + 1):
            yield (i << 4) | s_env_id


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
__s_env_gen__ = __s_env_gen()


def runtime_next() -> int:
    """``[COUNTER(80bit)]``"""
    return next(__runtime_gen__)


def local_next() -> int:
    """``[COUNTER(80bit)]``"""
    return next(__local_gen__)


def env_next() -> int:
    """``[COUNTER(72bit)][ENV-ID(8bit)]``"""
    return next(__env_gen__)


__t_env_gens__ = dict()


def thread_env_next() -> int:
    """``[COUNTER(72bit)][ENV-ID(8bit)]``"""
    i = threading.get_ident()
    if not (gen := __t_env_gens__.get(i)):
        gen = __t_env_gen()
        __t_env_gens__[i] = gen
    return next(gen)


def short_env_next() -> int:
    """``[COUNTER(4bit)][ENV-ID(4bit)]``"""
    return next(__s_env_gen__)

