from sys import version_info, platform
from time import get_clock_info
from time import gmtime
from time import struct_time
from time import time
from typing import Callable, TypeVar, Generic

_T = TypeVar("_T")
_NOT_FOUND = object()
_cache = dict()


class _cache_wrapper(Generic[_T]):
    def __init__(self, func: Callable[..., _T]): self.func = func

    def __call__(self, *args, **kwargs) -> _T:
        if (val := _cache.get(self.func.__name__, _NOT_FOUND)) is _NOT_FOUND:
            val = self.func(*args, **kwargs)
            _cache[self.func.__name__] = val
        return val


# #################################################################################
# CHECKS
# #################################################################################

@_cache_wrapper
def pyv() -> tuple[int, int]: return version_info[:2]


@_cache_wrapper
def _py_ge_3_11() -> bool: return not pyv() < (3, 11)


# =================================================================================
#   CLOCK CHECKS
# =================================================================================

# ---------------------------------------------------------------------------------
#       RESOLUTION
# ---------------------------------------------------------------------------------

@_cache_wrapper
def _clock_info_time(): return get_clock_info("time")


@_cache_wrapper
def clock_time_resolution() -> int:
    res = str(_clock_info_time().resolution)
    if "1e-" in res:
        return int(res[3:])    # 1e-03 -> 3
    else:
        return res.count("0")  # 0.001 -> 3


# =================================================================================
#   EPOCH CHECKS
# =================================================================================
# https://en.wikipedia.org/wiki/Epoch_(computing)

# ---------------------------------------------------------------------------------
#       EPOCH DEFINITION
# ---------------------------------------------------------------------------------
# [before python3.11]
# > ... On Windows and most Unix systems, the epoch is January 1, 1970, 00:00:00 (UTC) ...
# (https://docs.python.org/3.10/library/time.html#time.time)
# [since python3.11]
# > The epoch is the point where the time starts, the return value of time.gmtime(0).
# > It is January 1, 1970, 00:00:00 (UTC) on all platforms.
# (https://docs.python.org/3/library/time.html#epoch)

@_cache_wrapper
def _expected_epoch() -> struct_time: return struct_time((1970, 1, 1, 0, 0, 0, 3, 1, 0))  # January 1, 1970, 00:00:00 (UTC)


@_cache_wrapper
def _system_epoch() -> struct_time: return struct_time(gmtime(0)[:-1] + (0,))  # set [8]tm_isdst to 0  (https://docs.python.org/3/library/time.html#time.struct_time)


@_cache_wrapper
def system_epoch_recognized() -> bool:
    if not _py_ge_3_11():
        return _system_epoch() == _expected_epoch()
    return True


# ---------------------------------------------------------------------------------
#       THE YEAR 2038 PROBLEM - Y2K38 SUPERBUG (EPOCHALYPSE)
# ---------------------------------------------------------------------------------
# [32-bit systems]
# > The functions in this module may not handle dates and times before the epoch or far in the future.
# > The cut-off point in the future is determined by the C library; for 32-bit systems, it is typically in 2038.
# (https://docs.python.org/3/library/time.html#epoch)
# The relevance depends on the system architecture and the way seconds are stored in the system since the epoch.
# The highest dates that can be reached:
#   - January 19, 2038, 03:14:07 (UTC) on 32-bit system that stores the number as a signed integer
#   - February 7, 2106, 06:28:15 (UTC) on 32-bit system that stores the number as an unsigned integer
#   - ~292 billion years in the future on 64-bit system that stores the number as a signed integer
# (https://en.wikipedia.org/wiki/Year_2038_problem)

@_cache_wrapper
def _current_time_struct() -> struct_time: return gmtime(time())


@_cache_wrapper
def not_epochalypse() -> bool:
    return not _current_time_struct().tm_year < 2025  # (this condition is valid until ~2080)


# =================================================================================
#   RANDOM GENERATOR CHECKS
# =================================================================================

# ---------------------------------------------------------------------------------
#       URANDOM
# ---------------------------------------------------------------------------------
# [unix]
# > On a Unix-like system, random bytes are read from the /dev/urandom device.
# If the /dev/urandom device is not available or not readable, the NotImplementedError exception is raised.
# (https://docs.python.org/3/library/os.html#os.urandom)
# [windows before python3.11]
# > Changed in version 3.11: On Windows, BCryptGenRandom() is used instead of CryptGenRandom() which is deprecated.
# (https://docs.python.org/3/library/os.html#os.urandom)


@_cache_wrapper
def urandom_implemented() -> bool:
    try:
        from os import urandom as _ranb_
        if _ranb_(1) == _ranb_(1) and _ranb_(1) == _ranb_(1):
            raise SystemError
    except (ImportError, SystemError):
        return False
    return True


@_cache_wrapper
def not_depr_cryptgenrandom() -> bool:
    if not _py_ge_3_11():
        return not ("win" in platform and platform != "darwin")
    return True
