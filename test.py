from __future__ import annotations

import copy
import pickle
from datetime import datetime

try:
    import pathlib
    import sys
    sys.path.insert(0, str(pathlib.Path(__file__).parent))
except Exception:
    raise

import unittest

from src.ulid_tool import ulid


class TestULID(unittest.TestCase):

    def _test_interface(self, inter=ulid._ULIDInterface()):

        self.assertEqual(inter, inter.from_bytes(inter.bytes))
        self.assertEqual(inter, inter.from_int(inter.int))
        self.assertEqual(inter, inter.from_str(inter.str))
        self.assertEqual(inter, inter.from_codec(inter.codec))
        self.assertEqual(inter, inter.from_repr(inter.repr))
        self.assertEqual(inter, inter.from_hex(inter.hex))
        self.assertEqual(inter, inter.from_oct(inter.oct))
        self.assertEqual(inter, inter.from_bin(inter.bin))

        self.assertEqual(inter, inter.from_bytes(inter.bytes).bytes)
        self.assertEqual(inter, inter.from_int(inter.int).int)
        self.assertEqual(inter, inter.from_str(inter.str).str)
        self.assertEqual(inter, inter.from_codec(inter.codec).str)
        self.assertEqual(inter, inter.from_repr(inter.repr).repr)
        self.assertEqual(inter, inter.from_hex(inter.hex).hex)
        self.assertEqual(inter, inter.from_oct(inter.oct).oct)
        self.assertEqual(inter, inter.from_bin(inter.bin).bin)

        self.assertGreater(inter + 1, inter)
        self.assertLess(inter - 1, inter)

        ulid_copy = inter.copy()
        inter.this_forwards(10)
        self.assertGreater(inter, ulid_copy)
        inter.this_backwards(10)
        self.assertEqual(inter, ulid_copy)
        inter.this_backwards(10)
        self.assertLess(inter, ulid_copy)

        inter.this_forwards(11)
        self.assertEqual(inter, ulid_copy.next)
        self.assertEqual(inter.previous, ulid_copy)
        self.assertEqual(inter.previous.next, ulid_copy.next)

        inter.this_backwards(1)
        for i, _inter in enumerate(inter.igenerator(10), start=1):
            self.assertEqual(_inter, inter + i)

        new = pickle.loads(pickle.dumps(inter))
        self.assertEqual(inter, new)
        return new

    def test_ulid(self, ulid=ulid.ULID()):
        self._test_interface(self._test_interface(ulid))
        new = ulid.from_interfaces(copy.copy(ulid.timestamp), ulid.randomness.copy())
        self.assertEqual(ulid, new)
        self._test_interface(self._test_interface(new))

    def test_ulidtimestamp(self, timestamp=ulid.ULIDTimestamp()):
        self._test_interface(self._test_interface(timestamp))

        self.assertEqual(timestamp, timestamp.from_nanoseconds(timestamp.nanoseconds))
        self.assertEqual(timestamp, timestamp.from_milliseconds(timestamp.milliseconds))
        self.assertEqual(timestamp, timestamp.from_seconds(timestamp.seconds))
        self.assertEqual(timestamp, timestamp.from_datetime(timestamp.local_datetime))

        now = datetime.now()
        timestamp.local_datetime = now
        self.assertEqual(timestamp, timestamp.from_datetime(now))
        self.assertEqual(timestamp, timestamp.from_datetime(timestamp.utc_datetime))
        now = datetime(
            now.year,
            now.month,
            now.day,
            now.hour,
            now.minute,
            now.second,
            (now.microsecond // 1000) * 1000
        )
        self.assertEqual(timestamp.local_datetime, now)

    def test_ulidrandomness(self, randomness=ulid.ULIDRandomness()):
        self._test_interface(self._test_interface(randomness))

    def test_counters(self):
        self.assertEqual(ulid.ULID.runtime_lexical().randomness.int + 1, ulid.ULID.runtime_lexical().randomness.int)
        self.assertEqual(ulid.ULID.local_lexical().randomness.int + 1, ulid.ULID.local_lexical().randomness.int)
        self.assertEqual((ulid.ULID.env_lexical().randomness.int >> 8) + 1, (ulid.ULID.env_lexical().randomness.int >> 8))


if __name__ == '__main__':
    unittest.main()
