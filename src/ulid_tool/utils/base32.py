"""
Base32 data encodings

The contents of the functions are largely copied from the python standard library in version 3.13.

Modifications:
    - In contrast to the originals, the functions do not use some type checks.
    - Padding is outsourced from the encode function.
    - The parameter alphabet has been made available.
    - Interfaces for Crockford's base32 coding.
"""

import binascii


class alphabets:
    """
    - .std = b'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'
    - .hex = b'0123456789ABCDEFGHIJKLMNOPQRSTUV'
    - .crockford = b'0123456789ABCDEFGHJKMNPQRSTVWXYZ'
    """
    std = b'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'
    hex = b'0123456789ABCDEFGHIJKLMNOPQRSTUV'
    crockford = b'0123456789ABCDEFGHJKMNPQRSTVWXYZ'


_tab2 = {}
_rev = {}


def _encode(data: bytes, alphabet: bytes) -> tuple[bytearray, int]:
    # Delay the initialization of the table to not waste memory
    # if the function is never called
    if alphabet not in _tab2:
        tab = [bytes((i,)) for i in alphabet]
        _tab2[alphabet] = [a + b for a in tab for b in tab]
        tab = None
    # Pad the last quantum with zero bits if necessary
    leftover = len(data) % 5
    if leftover:
        data = data + b'\0' * (5 - leftover)  # Don't use += !
    encoded_a = bytearray()
    tab2 = _tab2[alphabet]
    for i in range(0, len(data), 5):
        c = int.from_bytes(data[i: i + 5], "big")
        encoded_a += (tab2[c >> 30] +           # bits 1 - 10
                    tab2[(c >> 20) & 0x3ff] +   # bits 11 - 20
                    tab2[(c >> 10) & 0x3ff] +   # bits 21 - 30
                    tab2[c & 0x3ff]             # bits 31 - 40
                   )
    return encoded_a, leftover


def encode(data: bytes, alphabet: bytes = alphabets.std) -> bytes:
    encoded_a, leftover = _encode(data, alphabet)
    # Adjust for any leftover partial quanta
    match leftover:
        case 1:
            encoded_a[-6:] = b'======'
        case 2:
            encoded_a[-4:] = b'===='
        case 3:
            encoded_a[-3:] = b'==='
        case 4:
            encoded_a[-1:] = b'='
        case 0:
            pass
        case _:
            raise ValueError(f"invalid {leftover=}")
    return bytes(encoded_a)


def encode_nopad(data: bytes, alphabet: bytes = alphabets.std) -> bytes:
    encoded_a, leftover = _encode(data, alphabet)
    # Adjust for any leftover partial quanta
    match leftover:
        case 1:
            encoded_a = encoded_a[:-6]
        case 2:
            encoded_a = encoded_a[:-4]
        case 3:
            encoded_a = encoded_a[:-3]
        case 4:
            encoded_a = encoded_a[:-1]
        case 0:
            pass
        case _:
            raise ValueError(f"invalid {leftover=}")
    return bytes(encoded_a)


def decode(data: bytes, alphabet: bytes = alphabets.std, casefold: bool = False, map01: bytes = None):
    # Delay the initialization of the table to not waste memory
    # if the function is never called
    if alphabet not in _rev:
        _rev[alphabet] = {v: k for k, v in enumerate(alphabet)}
    # Handle section 2.4 zero and one mapping.  The flag map01 will be either
    # False, or the character to map the digit 1 (one) to.  It should be
    # either L (el) or I (eye).
    if map01 is not None:
        assert len(map01) == 1, repr(map01)
        data = data.translate(bytes.maketrans(b'01', b'O' + map01))
    if casefold:
        data = data.upper()
    # Strip off pad characters from the right.  We need to count the pad
    # characters because this will tell us how many null bytes to remove from
    # the end of the decoded string.
    assert (data_len := len(data)) > 1, repr(data)
    data = data.rstrip(b'=')
    # Now decode the full quanta
    decoded = bytearray()
    rev = _rev[alphabet]
    for i in range(0, len(data), 8):
        quanta = data[i: i + 8]
        acc = 0
        try:
            for c in quanta:
                acc = (acc << 5) + rev[c]
        except KeyError:
            raise binascii.Error('Non-base32 digit found') from None
        decoded += acc.to_bytes(5, "big")  # big endian
    # Process the last, partial quanta
    if padchars := data_len % 8:
        padchars = 8 - padchars
        if padchars not in {0, 1, 3, 4, 6}:
            raise binascii.Error(f'Incorrect padding {padchars=}')
        elif decoded:
            acc <<= 5 * padchars
            last = acc.to_bytes(5, "big")  # big endian
            leftover = (43 - 5 * padchars) // 8  # 1: 4, 3: 3, 4: 2, 6: 1
            decoded[-5:] = last[:leftover]
    return bytes(decoded)


def encode_hex(data): return encode(data, alphabets.hex)
def encode_hex_nopad(data): return encode_nopad(data, alphabets.hex)


def decode_hex(data, casefold=False):
    # base32hex does not have the 01 mapping
    return decode(data, alphabets.hex, casefold)


def encode_crockford(data): return encode(data, alphabets.crockford)
def encode_crockford_nopad(data): return encode_nopad(data, alphabets.crockford)


def decode_crockford(data, casefold=False):
    # Crockford's base32 does not have the 01 mapping
    return decode(data, alphabets.crockford, casefold)
