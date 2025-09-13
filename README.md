```console
python3 -m pip install ulid_tool --upgrade
```


# Tool for Unique Lexicographically Identifier (ULID)


> \>>> [**SLID**](#Short-Unique-Lexicographically-Identifier-SLID) 
> (A shorter, meaningful ID inspired by ULID (included in this package)) <<<


### [Original title] Unique Lexicographically Sortable Identifier

ULID is a widely used specification for identifiers which, 
unlike UUID, aims for readability, anonymity, compatibility, 
and practical use through sortability.
(Original specification: [https://github.com/ulid/spec](https://github.com/ulid/spec))

By modifying the original specification, this implementation enables 
the generation of guaranteed unique ULIDs within a file system.

> The ULID specification does not achieve guaranteed cross-system uniqueness. 
> Even the widely used UUID versions cannot achieve absolute uniqueness, 
> even though they are considered unique in practice. 
> [This project](https://github.com/UN8ID/UN8ID) 
> deals with the highest possible uniqueness in time and space with the highest possible anonymity.

## Statute

- This module implements the original specification and is extended 
  by modifications that follow the idea and properties.
- The module contains utils as separate modules/functions/methods 
  for the creation or handling of ULIDs.
- The module contains system integrity checks for the consistent creation of ULIDs.
- Python type checks during runtime are not performed.


## Properties and basic concept

### UUID vs ULID

#### Properties of a UUID

Depending on the version, a UUID can consist of
- **Timestamp**
- **The Mac address** 

  The use of a MAC address can be considered sensitive information about the creator that is being disclosed.

- **Random values**

  Random values can never be considered absolutely unique. Even though the probability of two identical UUIDv4s occurring is practically zero. Furthermore, random values naturally do not carry any information.

- **A centrally managed seed**

  A central, generally recognized authority is required.


#### Properties of a ULID

- 128-bit compatibility with UUID
- 1.21e+24 unique ULIDs per millisecond
- Lexicographically **sortable**
- Canonically encoded as a **26 character string**, as opposed to the 36 character UUID
- Uses **Crockford's base32** for better efficiency and readability (5 bits per character)
- **Case insensitive**
- No special characters (**URL safe**)
- **Monotonic sort order** (correctly detects and handles the same millisecond)



### Binary Layout (original specification)

A ULID has a fixed length of 128 bits coded in 16 bytes/octets and consists of
2 components. Each component is coded in big-endian
format (network byte order).

```
      0                   1                   2                   3
      0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
     |               |               |               |               |
     +---------------------------------------------------------------+
     | ms since epoch                                                |
     + - - - - - - - - - - - - - - - +-------------------------------+
     | ...                           | randomnes                     |
     +-------------------------------+ - - - - - - - - - - - - - - - +
     | ...                                                           |
     + - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - +
     | ...                                                           |
     +---------------------------------------------------------------+
```


### Variations

_**ULID.runtime_lexical**_

Replaces the random part with a monotonic counter that counts up from 0 within a runtime and automatically restarts when the space is used up.
**Not thread-safe**.


_**ULID.local_lexical**_

Similar to runtime_lexical. Reads the last status of the counter from the file system and writes the status when the Python interpreter terminates.
**Not thread-safe**.


_**ULID.env_lexical**_

Here, the random part consists of 8 bits from a one-time read ID per interpreter start + 72 bits of a monotonic counter.
**Not sub-thread or sub-process safe.** However, for up to 256 simultaneously running main processes.


_**ULID.thread_env_lexical**_

Structured like env_lexical. Here, the thread ID is used for system-wide uniqueness.
**Thread-safe**.


_**ULID.short_env_lexical**_

Heavily modified version. The random part consists of only 8 bits. 
4 bits from a uniquely read ID per 
interpreter start + 4 bits from a monotonic counter.
**Not sub-thread or sub-process safe.** However, for up to 16 simultaneously running main processes.



# Short Unique Lexicographically Identifier (SLID)

SLID is based on the fundamental concept of ULID.

The timestamp is identical to that of ULID. 
The random part has been reduced to 2 bytes, 
consisting of an uniquely read ID per 
interpreter start (first byte) and a 
monotonic counter (second byte). Unlike ULID, 
where this part is also encoded with base32 
for strings, in SLID the value is simply given 
in hexadecimal for better readability.

A SLID has a fixed length of 64 bits coded in 8 bytes/octets and consists of
2 components. Each component is coded in big-endian
format (network byte order).

```
      0                   1                   2                   3
      0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
     |               |               |               |               |
     +---------------------------------------------------------------+
     | ms since epoch                                                |
     + - - - - - - - - - - - - - - - +-------------------------------+
     | ...                           | randomnes                     |
     +-------------------------------+-------------------------------+
```

**Not sub-thread or sub-process safe.** However, for up to 256 simultaneously running main processes.


# Module usages

```python
if bypass_checks:
    # By default, several system integrity checks are performed during import. 
    # To bypass this, the following code can be used
    import ulid_tool
    ulid_tool.SYSTEM_CHECKS = False
    from ulid_tool.ulid import ULID, SLID
else:
    from ulid_tool.ulid import ULID, SLID

# ULID of ORIGINAL SPECIFICATION
ulid = ULID()

# VARIATIONS
ULID.runtime_lexical()
ULID.local_lexical()
ULID.env_lexical()
ULID.thread_env_lexical()
ULID.short_env_lexical()
## SLID
SLID()

# INTERFACES

## CONVERSIONS
ulid.bytes
ulid.int
ulid.str
ulid.codec
ulid.repr
ulid.hex
ulid.oct
ulid.bin

## PARTS
ulid.randomness
ulid.timestamp
ulid.prime

## CREATE FROM
ulid.from_interfaces(ulid.timestamp, ulid.randomness)
ulid.from_codec(ulid.codec)
ulid.from_bytes(ulid.bytes)
ulid.from_str(ulid.str)
ulid.from_int(ulid.int)
ulid.from_hex(ulid.hex)
ulid.from_oct(ulid.oct)
ulid.from_bin(ulid.bin)
ulid.from_repr(ulid.repr)
### UTIL
ulid.prime_from_type_of(ulid.oct)

## PROGRESSION
assert ulid.copy().this_forwards(n=1) == ulid.next
assert ulid.copy().this_backwards(n=1) == ulid.previous
ulid.igenerator(ni=3)
reversed(ulid.igenerator(ni=3))
```


