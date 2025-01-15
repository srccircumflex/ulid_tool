from __future__ import annotations

import builtins
from abc import abstractmethod
from typing import Any, Generator, Reversible, TypeVar

try:
    from typing_extensions import Self
except ImportError:
    from typing import Any as Self


_int = builtins.int
_bytes = builtins.bytes
_str = builtins.str


class _Interface:
    prime: Any

    @property
    @abstractmethod
    def bytes(self) -> _bytes:
        raise NotImplementedError(self.__class__)

    @bytes.setter
    @abstractmethod
    def bytes(self, val: _bytes):
        ...

    @property
    def int(self) -> _int:
        return int.from_bytes(self.bytes, "big")

    @int.setter
    @abstractmethod
    def int(self, val: _int):
        ...

    @property
    def str(self) -> _str:
        return self.bytes.decode()

    @str.setter
    @abstractmethod
    def str(self, val: _str):
        ...

    @property
    def repr(self) -> _str:
        return repr(self.str)

    @repr.setter
    @abstractmethod
    def repr(self, val: _str):
        ...

    @property
    def hex(self) -> _str:
        return hex(self.int)

    @hex.setter
    def hex(self, val: _str):
        self.int = int(val, 16)

    @property
    def oct(self) -> _str:
        return oct(self.int)

    @oct.setter
    def oct(self, val: _str):
        self.int = int(val, 8)

    @property
    def bin(self) -> _str:
        return bin(self.int)

    @bin.setter
    def bin(self, val: _str):
        self.int = int(val, 2)

    def __bytes__(self) -> _bytes:
        return self.bytes

    def __str__(self) -> _str:
        return self.str

    def __int__(self) -> _int:
        return self.int

    def __hex__(self) -> _str:
        return self.hex

    def __oct__(self) -> _str:
        return self.oct

    def __bin__(self) -> _str:
        return self.bin

    def __repr__(self) -> _str:
        return self.repr

    def __hash__(self) -> _int:
        return self.int

    def __getstate__(self):
        return self.prime

    def __setstate__(self, state):
        self.prime = state

    @classmethod
    def from_bytes(cls, val: _bytes) -> Self:
        new = cls.__new__(cls)
        new.bytes = val
        return new

    @classmethod
    def from_str(cls, val: _str) -> Self:
        new = cls.__new__(cls)
        new.str = val
        return new

    @classmethod
    def from_int(cls, val: _int) -> Self:
        new = cls.__new__(cls)
        new.int = val
        return new

    @classmethod
    def from_hex(cls, val: _str) -> Self:
        new = cls.__new__(cls)
        new.hex = val
        return new

    @classmethod
    def from_oct(cls, val: _str) -> Self:
        new = cls.__new__(cls)
        new.oct = val
        return new

    @classmethod
    def from_bin(cls, val: _str) -> Self:
        new = cls.__new__(cls)
        new.bin = val
        return new

    @classmethod
    def from_repr(cls, val: _str) -> Self:
        new = cls.__new__(cls)
        new.repr = val
        return new

    def copy(self) -> Self:
        new = self.__class__.__new__(self.__class__)
        new.prime = self.prime
        return new

    def __copy__(self):
        return self.copy()

    def __add__(self, n: _int) -> Self:
        new = self.copy()
        new.int += n
        return new

    def __sub__(self, n: _int) -> Self:
        new = self.copy()
        new.int -= n
        return new

    def this_forwards(self, n: int):
        self.int += n

    def this_backwards(self, n: int):
        self.int -= n

    @property
    def next(self) -> Self:
        return self + 1

    @property
    def previous(self) -> Self:
        return self - 1

    def igenerator(self, ni: _int | None) -> _IGenerator[Self]:
        """
        This method returns a blunt (reversible) iterator that simply in(de)creases the integer
        value by 1 for each iteration and returns a new object.

        :param ni: specifies a number of iterations. If None is passed, iteration is infinite, buffer overflows and
          cancellation should be handled externally.
        """
        return _IGenerator(self, ni)

    def prime_from_type_of(self, obj: object):
        if isinstance(obj, type(self.prime)):
            return self.prime
        if isinstance(obj, int):
            return self.int
        if isinstance(obj, (bytes, bytearray, memoryview)):
            return self.bytes
        if isinstance(obj, str):
            if obj.startswith("0x"):
                return self.hex
            if obj.startswith("0o"):
                return self.oct
            if obj.startswith("0b"):
                return self.bin
            if obj.startswith("<"):
                return self.repr
            else:
                return self.str
        return NotImplemented

    def __eq__(self, other: _Interface) -> bool:
        if isinstance(other, _Interface):
            return self.prime == other.prime
        else:
            return self.prime_from_type_of(other) == other

    def __ne__(self, other: _Interface) -> bool:
        if isinstance(other, _Interface):
            return self.prime != other.prime
        else:
            return self.prime_from_type_of(other) != other

    def __lt__(self, other: _Interface) -> bool:
        if isinstance(other, _Interface):
            return self.prime < other.prime
        else:
            return self.prime_from_type_of(other) < other

    def __gt__(self, other: _Interface) -> bool:
        if isinstance(other, _Interface):
            return self.prime > other.prime
        else:
            return self.prime_from_type_of(other) > other

    def __le__(self, other: _Interface) -> bool:
        if isinstance(other, _Interface):
            return self.prime <= other.prime
        else:
            return self.prime_from_type_of(other) <= other

    def __ge__(self, other: _Interface) -> bool:
        if isinstance(other, _Interface):
            return self.prime >= other.prime
        else:
            return self.prime_from_type_of(other) >= other


_T = TypeVar("_T")


class _IGenerator(Reversible[_T]):

    def __init__(self, interface: _Interface, ni: int):
        self.interface = interface
        self.ni = ni

    def __iter__(self) -> Generator[_T]:
        if self.ni is not None:
            def gen():
                _next = self.interface + 1
                for i in range(self.ni):
                    yield _next
                    _next += 1
        else:
            def gen():
                _next = self.interface + 1
                while True:
                    yield _next
                    _next += 1
        return gen()

    def __reversed__(self) -> Generator[_T]:
        if self.ni is not None:
            def gen():
                _next = self.interface - 1
                for i in range(self.ni):
                    yield _next
                    _next -= 1
        else:
            def gen():
                _next = self.interface - 1
                while True:
                    yield _next
                    _next -= 1
        return gen()
