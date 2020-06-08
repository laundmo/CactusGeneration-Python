#cython: language_level=3
import time
import math
import cython
cdef long long _seed = 0

cpdef set_seed(long long seed):
    global _seed
    _seed = (seed ^ 0x5deece66d) & ((1 << 48) - 1)

cdef next(long long bits):
    global _seed

    if bits < 1:
        bits = 1
    elif bits > 32:
        bits = 32

    _seed = (_seed * 0x5deece66d + 0xb) & ((1 << 48) - 1)
    cdef long long retval = _seed >> (48 - bits)

    # Python and Java don't really agree on how ints work. This converts
    # the unsigned generated int into a signed int if necessary.
    if retval & (1 << 31):
        retval -= (1 << 32)

    return retval

cpdef nextInt(long long n):
    global _seed
    if n is None:
        return next(32)

    if n <= 0:
        raise ValueError("Argument must be positive!")

    # This tricky chunk of code comes straight from the Java spec. In
    # essence, the algorithm tends to have much better entropy in the
    # higher bits of the seed, so this little bundle of joy is used to try
    # to reject values which would be obviously biased. We do have an easy
    # out for power-of-two n, in which case we can call next directly.

    # Is this a power of two?
    if not (n & (n - 1)):
        return (n * next(31)) >> 31

    cdef long long bits = next(31)
    cdef long long val = bits % n
    while (bits - val + n - 1) < 0:
        bits = next(31)
        val = bits % n

    return val