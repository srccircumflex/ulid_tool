from __future__ import annotations

import builtins
import datetime
try:
    from typing_extensions import Self
except ImportError:
    from typing import Any as Self


from ..utils import time_ms
from ..utils import _randb
from ..utils import base32
from ..utils import lexical_rand
from ..utils.baseinterface import _Interface


from .. import SYSTEM_CHECKS
if SYSTEM_CHECKS:
    from ..utils import system_checks as _system_checks
    from warnings import warn

    class _SystemIntegrity:
        ok: bool = True
        clock_time_resolution: int = _system_checks.clock_time_resolution()
        if clock_time_resolution < 3:
            ok = False
            warn(f"\n"
                 f"The clock on this system does not supports millisecond resolution.\n"
                 f"Resolution is {clock_time_resolution}."
                 )
        system_epoch_recognized: bool = _system_checks.system_epoch_recognized()
        if not system_epoch_recognized:
            ok = False
            warn(f"\n"
                 f"The epoch in this system is - contrary to most - not defined as `January 1, 1970, 00:00:00 (UTC)' "
                 f"(https://en.wikipedia.org/wiki/Epoch_(computing)).\n"
                 f"The ULID specification stipulates this date.\n"
                 f"(As of version 3.11, this standard is ensured by Python. "
                 f"Version is: {'%d.%d' % _system_checks.pyv()})"
                 )
        urandom_implemented: bool = _system_checks.urandom_implemented()
        if not urandom_implemented:
            ok = False
            warn("\n"
                 "os.urandom not available!\n"
                 "Cryptographic invalid methods are used!\n"
                 "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
                 )
        not_depr_cryptgenrandom: bool = _system_checks.not_depr_cryptgenrandom()
        if not not_depr_cryptgenrandom:
            warn(f"\n"
                 f"Python3 versions < 3.11 on Windows uses the deprecated `CryptGenRandom()' instead of `BCryptGenRandom()'. "
                 f"(Version is: {'%d.%d' % _system_checks.pyv()})\n"
                 f"If no warning about os.urandom has been issued, this is currently not a problem.",
                 )
        not_epochalypse: bool = _system_checks.not_epochalypse()
        if not not_epochalypse:
            ok = False
            warn("\n"
                 "⋆✴︎°｡⋆⋆✴︎°｡⋆⋆✴︎°｡⋆⋆✴︎°｡⋆⋆✴︎°｡⋆⋆✴︎°｡⋆⋆✴︎°｡\n"
                 "   Y2K38 superbug (Epochalypse)\n"
                 "⋆✴︎°｡⋆⋆✴︎°｡⋆⋆✴︎°｡⋆⋆✴︎°｡⋆⋆✴︎°｡⋆⋆✴︎°｡⋆⋆✴︎°｡"
                 )

    systemIntegrity = _SystemIntegrity()


_int = builtins.int
_bytes = builtins.bytes
_str = builtins.str


class _ULIDInterface(_Interface):
    prime: _int | _bytes | tuple[_int, _bytes]

    @property
    def str(self) -> _str:
        return self.codec.decode()

    @str.setter
    def str(self, val: _str):
        self.codec = val.encode()

    @property
    def repr(self) -> _str:
        return f"<{self.__class__.__name__} {self.str}>"

    @repr.setter
    def repr(self, val: _str):
        self.str = val.split(" ")[1][:-1]

    @property
    def codec(self) -> _bytes:
        return base32.encode_crockford_nopad(self.bytes)

    @codec.setter
    def codec(self, val: _bytes):
        self.bytes = base32.decode_crockford(val)

    @classmethod
    def from_codec(cls, val: _bytes) -> Self:
        new = cls.__new__(cls)
        new.codec = val
        return new


class ULIDTimestamp(_ULIDInterface):
    prime: _int
    n: _int = 6

    @property
    def bytes(self) -> _bytes:
        return self.prime.to_bytes(self.n, "big")

    @bytes.setter
    def bytes(self, val: _bytes):
        self.int = int.from_bytes(val, "big")

    @property
    def int(self) -> _int:
        return self.prime

    @int.setter
    def int(self, val: _int):
        self.prime = val

    @property
    def nanoseconds(self) -> _int:
        return self.prime * 1_000_000

    @nanoseconds.setter
    def nanoseconds(self, val: _int):
        self.prime = val // 1_000_000

    @classmethod
    def from_nanoseconds(cls, val: float) -> ULIDTimestamp:
        new = cls.__new__(cls)
        new.nanoseconds = val
        return new

    @property
    def milliseconds(self) -> _int:
        return self.prime

    @milliseconds.setter
    def milliseconds(self, val: _int):
        self.prime = val

    @classmethod
    def from_milliseconds(cls, val: _int):
        new = cls.__new__(cls)
        new.milliseconds = val
        return new

    @property
    def seconds(self) -> builtins.float:
        return self.prime / 1000

    @seconds.setter
    def seconds(self, val: builtins.float):
        self.prime = int(val * 1000)

    @classmethod
    def from_seconds(cls, val: float) -> ULIDTimestamp:
        new = cls.__new__(cls)
        new.seconds = val
        return new

    @property
    def local_datetime(self) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(self.seconds)

    @local_datetime.setter
    def local_datetime(self, val: datetime.datetime):
        self.seconds = val.timestamp()

    @property
    def utc_datetime(self) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(self.seconds, datetime.timezone.utc)

    @utc_datetime.setter
    def utc_datetime(self, val: datetime.datetime):
        self.seconds = val.timestamp()

    @classmethod
    def from_datetime(cls, val: datetime.datetime) -> ULIDTimestamp:
        new = cls.__new__(cls)
        new.utc_datetime = val
        return new

    def __init__(self):
        self.prime = time_ms()


class ULIDRandomness(_ULIDInterface):
    prime: _bytes
    n: _int = 10

    @property
    def bytes(self) -> _bytes:
        return self.prime

    @bytes.setter
    def bytes(self, val: _bytes):
        self.prime = val

    @property
    def int(self) -> _int:
        return int.from_bytes(self.prime, "big")

    @int.setter
    def int(self, val: _int):
        self.prime = val.to_bytes(self.n, "big")

    def __init__(self):
        self.prime = _randb(10)

    @classmethod
    def runtime_lexical(cls):
        """Next value of the monotonic runtime counter."""
        new = cls.__new__(cls)
        new.int = lexical_rand.runtime_next()
        return new

    @classmethod
    def local_lexical(cls):
        """Next value of the monotonic local counter."""
        new = cls.__new__(cls)
        new.int = lexical_rand.local_next()
        return new

    @classmethod
    def env_lexical(cls):
        """Next value of the monotonic env counter."""
        new = cls.__new__(cls)
        new.int = lexical_rand.env_next()
        return new

    @classmethod
    def thread_env_lexical(cls):
        """Next value of the monotonic thread-env counter."""
        new = cls.__new__(cls)
        new.int = lexical_rand.thread_env_next()
        return new

    @classmethod
    def short_env_lexical(cls):
        """Next value of the monotonic short-env counter."""
        new = cls.__new__(cls)
        new.n = 1
        new.int = lexical_rand.short_env_next()
        return new


class ULID(_ULIDInterface):

    @property
    def prime(self) -> tuple[_int, _bytes]: 
        return self.timestamp.prime, self.randomness.prime

    @prime.setter
    def prime(self, val: tuple[_int, _bytes]):
        self.timestamp = ULIDTimestamp.from_milliseconds(val[0])
        self.randomness = ULIDRandomness.from_bytes(val[1])
    
    timestamp: ULIDTimestamp
    randomness: ULIDRandomness

    @property
    def n(self) -> _int:
        return self.timestamp.n + self.randomness.n

    @property
    def bytes(self) -> _bytes:
        return self.timestamp.bytes + self.randomness.bytes

    @bytes.setter
    def bytes(self, val: _bytes):
        self.timestamp.bytes = val[:6]
        self.randomness.bytes = val[6:]

    @property
    def int(self) -> _int:
        return int.from_bytes(self.bytes, "big")

    @int.setter
    def int(self, val: _int):
        self.bytes = val.to_bytes(self.n, "big")

    @property
    def str(self) -> _str:
        return self.codec.decode()

    @str.setter
    def str(self, val: _str):
        self.timestamp.str = val[:10]
        self.randomness.str = val[10:]

    @property
    def codec(self) -> _bytes:
        return self.timestamp.codec + self.randomness.codec

    @codec.setter
    def codec(self, val: _bytes):
        self.timestamp.codec = val[:10]
        self.randomness.codec = val[10:]

    def __new__(cls) -> ULID:
        new = super().__new__(cls)
        new.timestamp = ULIDTimestamp.__new__(ULIDTimestamp)
        new.randomness = ULIDRandomness.__new__(ULIDRandomness)
        return new

    def __init__(self):
        self.timestamp = ULIDTimestamp()
        self.randomness = ULIDRandomness()

    @classmethod
    def from_interfaces(cls, timestamp: ULIDTimestamp, randomness: ULIDRandomness):
        new = cls.__new__(cls)
        new.timestamp = timestamp
        new.randomness = randomness
        return new

    @classmethod
    def runtime_lexical(cls):
        """Creates the random part using a monotonic counter that starts from 0 for each runtime.
        **(not thread save)**

        ``[TIMESTAMP(48bit|6bytes)][COUNTER(80bit|10bytes)]``"""
        return cls.from_interfaces(ULIDTimestamp(), ULIDRandomness.runtime_lexical())

    @classmethod
    def local_lexical(cls):
        """Creates the random part with a monotonic counter that reads the last state from a local file.
        The new state is saved after the interpreter has finished.
        **(not thread save)**

        ``[TIMESTAMP(48bit|6bytes)][COUNTER(80bit|10bytes)]``"""
        return cls.from_interfaces(ULIDTimestamp(), ULIDRandomness.local_lexical())

    @classmethod
    def env_lexical(cls):
        """Creates the random part using two monotonic counters.
        The first 8 bits of the random part are set by a counter that reads the last status for each runtime and saves it directly (env id).
        The rest is set analogous to the runtime counter.
        **(thread safe up to 255 simultaneous INDEPENDENT threads)**

        ``[TIMESTAMP(48bit|6bytes)][ENV-ID(8bit|1byte)][COUNTER(72bit|9bytes)]``"""
        return cls.from_interfaces(ULIDTimestamp(), ULIDRandomness.env_lexical())

    @classmethod
    def thread_env_lexical(cls):
        """Creates the random part using two monotonic counters.
        The first 8 bits of the random part are set by a counter that reads the last status for each tread identifier and saves it directly.
        The rest is set analogous to the runtime counter.
        **(thread safe up to 255 simultaneous [sub]threads or [sub]processes)**

        ``[TIMESTAMP(48bit|6bytes)][ENV-ID(8bit|1byte)][COUNTER(72bit|9bytes)]``"""
        return cls.from_interfaces(ULIDTimestamp(), ULIDRandomness.thread_env_lexical())

    @classmethod
    def short_env_lexical(cls):
        """**SHORT VERSION (not compatible with the origin specification, backward compatibility not implemented)**

        Replaces the random part with a short counter (8bit|1byte).
        The short environment counter consists of half an environment counter and half a call counter.
        **(thread safe up to 16 simultaneous INDEPENDENT threads)**

        ``[TIMESTAMP(48bit|6bytes)][ENV-ID(4bit|.5byte)][COUNTER(4bit|.5byte)]``"""
        return cls.from_interfaces(ULIDTimestamp(), ULIDRandomness.short_env_lexical())


class SLIDRandomness(ULIDRandomness):
    prime: _bytes
    n: _int = 2

    def __init__(self):  # noqa: super().__init__() missed
        self.int = lexical_rand.slid_next()

    @property
    def codec(self) -> _bytes:
        return f"{hex(self.int)[2:].upper():0>4}".encode()

    @codec.setter
    def codec(self, val: _bytes):
        self.int = int(val, 16)


class SLID(ULID):

    def __init__(self):  # noqa: super().__init__() missed
        self.timestamp = ULIDTimestamp()
        self.randomness = SLIDRandomness()


MIN_TIMESTAMP: ULIDTimestamp = ULIDTimestamp.from_bytes(b'\x00\x00\x00\x00\x00\x00')  # 0
MAX_TIMESTAMP: ULIDTimestamp = ULIDTimestamp.from_bytes(b'\xff\xff\xff\xff\xff\xff')  # 281,474,976,710,655
MIN_RANDOMNESS: ULIDRandomness = ULIDRandomness.from_bytes(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')  # 0
MAX_RANDOMNESS: ULIDRandomness = ULIDRandomness.from_bytes(b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff')  # 1,208,925,819,614,629,174,706,175
MIN_ULID: ULID = ULID.from_interfaces(MIN_TIMESTAMP, MIN_RANDOMNESS)  # 0
MAX_ULID: ULID = ULID.from_interfaces(MAX_TIMESTAMP, MAX_RANDOMNESS)  # 340,282,366,920,938,463,463,374,607,431,768,211,455


def millisecond_to_bytes(t: int):
    """t.to_bytes(6, "big")"""
    return t.to_bytes(6, "big")


def millisecond_from_bytes(t: bytes):
    """int.from_bytes(t, "big")"""
    return int.from_bytes(t, "big")


def validate_timestamp_len(t: str | bytes) -> bool:
    """len(t) == 10"""
    return len(t) == 10


def validate_randomness_len(r: str | bytes) -> bool:
    """len(r) == 16"""
    return len(r) == 16


def validate_ulid_len(ulid: str | bytes) -> bool:
    """len(ulid) == 26"""
    return len(ulid) == 26


def build(t: bytes, r: bytes) -> bytes:
    """base32.encode_crockford_nopad(t) + base32.encode_crockford_nopad(r)"""
    return base32.encode_crockford_nopad(t) + base32.encode_crockford_nopad(r)


def plain():
    """build(millisecond_to_bytes(time_ms()), _randgen(10))"""
    return build(millisecond_to_bytes(time_ms()), _randb(10))


def plain_from_seconds(t: float):
    """build(millisecond_to_bytes(int(t * 1000)), _randgen(10))"""
    return build(millisecond_to_bytes(int(t * 1000)), _randb(10))


def plain_from_milliseconds(t: int):
    """build(millisecond_to_bytes(t), _randgen(10))"""
    return build(millisecond_to_bytes(t), _randb(10))


def split(ulid: str | bytes) -> tuple[str | bytes, str | bytes]:
    """ulid[:10], ulid[10:]"""
    return ulid[:10], ulid[10:]


def reverse(ulid: bytes) -> tuple[bytes, bytes]:
    """tuple(base32.decode_crockford(x) for x in split(ulid))"""
    return tuple(base32.decode_crockford(x) for x in split(ulid))

