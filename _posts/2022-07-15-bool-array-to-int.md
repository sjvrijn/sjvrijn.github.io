---
layout: post
title:  "Boolean Array to (gmpy2) int"
date:   2022-07-15 07:00:00 +0200
tags: python timing speedup optimization perfplot
---

This time another colleague was trying to work with [`gmpy2`], a library for
fast arithmetic operations on very large numbers. The specific problem was that
the numbers had to be created from a numpy array with 1,000,000 booleans or more
first, and the method my colleague had come up with wasn't fast enough.


## To beat: num = num.bit_set(i)

As a first attempt, they created a `gmpy2.mpz` object and manually set each bit
with the [`bit_set()`] method.

```python
import gmpy2

def mpz_by_bitset(bool_array):
    num = gmpy2.mpz(0)
    for i, bit in enumerate(bool_array[::-1]):
        if bit:
            num = num.bit_set(i)
    return num
```

Before considering performance on large arrays, let's test it with a sample of
128 (=2^7) booleans:

```python
import numpy as np
bool_array = np.random.randint(0,2,2**7, dtype=bool)
%timeit mpz_by_bitset(bool_array)
```
> 10.8 µs ± 4.13 ns per loop (mean ± std. dev. of 7 runs, 100,000 loops each)

This function does what we want, but raises two red flags for me:
- We're processing **every** bit individually
- A new copy of the object is made every time we change a bit

Modern processors work on 64 bits at a time, or possibly even more with vector
instructions, so only working on a single bit at a time means we're using only
about 1-2% of our processor's power.


## First Suggestion: making a binary string

In a first attempt to do better, we make use of the fact that Python's integers
can be [infinitely large], and can be created from a [binary string]. We first
manually create the binary string with `''.join()`, create a Python int and then
pass that to `gmpy2`:

```python
def mpz_by_bin_string(bool_array):
    bin_string = '0b' + ''.join(map(str, bool_array.astype(int)))    
    return gmpy2.mpz(int(bin_string, base=2))
    
%timeit mpz_by_bin_string(bool_array)
```
> 80.2 µs ± 85.4 ns per loop (mean ± std. dev. of 7 runs, 10,000 loops each)

While this may seem more Pythonic, we're now working with bits as a string
instead of as numbers. This isn't great for performance, and it shows: for our
128-bit example it's about 8x slower.


## Second Suggestion: numpy.packbits

With our first suggestion we are in the right direction though: a number in a
computer is after all just a string of bits in memory. The only thing we want to
do is take this string of bits we have, our boolean array, and let gmpy2 read it
as a number it recognizes. So rather than doing this via a string as an
intermediate step, we should just do this numerically. As `gmpy2` has a method
`from_binary`, this should be possible.

The problem is that a boolean in Python/numpy is stored as an integer, taking up
at least one byte of space ('00000000' or '00000001'). Simply sticking those
behind eachother will give us a number with a lot of zeros in the middle that
don't belong there: we only care about the last bit.

That problem can be solved with [`numpy.packbits`], which packs an array of
binary values into an array of type `uint8` = 1 byte per value. That gets rid of
all the zeros we don't want. Now we can use numpy's [`tobytes()`] to get the
array directly as bytes.

Sadly, that solution fails in practise. While [`gmpy2.from_binary()`] accepts a
bytestring as input, it fails when given the result of our bitpacked array as
bytes. There seems to be some special formatting needed that isn't documented.
We need to use a Python integer as an intermediate for it to work:

```python
def mpz_by_packbits(bool_array):
    bytestring = np.packbits(bool_array).tobytes()
    python_int = int.from_bytes(bytestring, byteorder='big')
    return gmpy2.mpz(python_int)

%timeit mpz_by_packbits(bool_array)
```
> 1.54 µs ± 10.2 ns per loop (mean ± std. dev. of 7 runs, 1,000,000 loops each)

Now that's more like it! Even with the added step of using `int.from_bytes`
instead of directly using `gmpy2.from_binary`, we're still over 6x faster. But
does that hold up for larger array sizes?


## Automated Comparison with Perfplot

[Perfplot] is a cool little package that automates the creation of timing
comparison plots like those I manually made in [earlier][1] [posts][2]. Using it
we can quickly compare the different implementations and see how they scale. As
test input size, I will use only multiples of complete bytes, just to prevent
any possible issues with [`numpy.packbits`].

```python
import perfplot

out = perfplot.bench(
    setup=lambda n: np.random.randint(0,2,2**n),
    kernels=[mpz_by_bitset, mpz_by_bin_string, mpz_by_packbits],
    n_range=[n for n in range(3, 36, 4)],
    labels=['mpz.bit_set', 'int(bin_string)', 'np.packbits'],
    xlabel='2^n booleans',
    equality_check=False,
    max_time=20,
)

out.show(logy=True, logx=False)
```
![](/img/gmpy2_from_boolarray.svg)

The most obvious thing to notice is that the `np.packbits` version is clearly
the fastest and scales best with larger sizes. It only takes about 10 seconds
for an array of 2^30 booleans. That's almost 1 GigaByte of memory for just the
final bits!

The `int(bin_string)` version scales about the same as `np.packbits`, but is
a lot slower overall. I can imagine the translation back and forth from integers
to strings and back into an integer taking up a lot of overhead.

The `bit_set` version doesn't actually perform too bad up to ~2^17 booleans, or
about 16 KiloBytes. After that it scales a lot more poorly and does worse than
even the `int(bin_string)` implementation. Perhaps the local copies that keep
getting made are overflowing the processor's cache at that point? Either way, it
exceeds a runtime of 100 seconds when processing 2^23 booleans (=one MegaByte).


## Conclusion

Iterating over the individual bits and using `bit_set` is indeed slower than the
implementation using `np.packbits`, and scales surprisingly poorly for more than
2^17 booleans.

Also: [Perfplot] is cool!



---

[1]: /2019/10/05/numpy-indexing
[2]: /2021/11/14/case-study-1

[`bit_set()`]: https://gmpy2.readthedocs.io/en/latest/mpz.html#mpz-methods
[infinitely large]: https://docs.python.org/3/library/stdtypes.html?highlight=unlimited%20precision#numeric-types-int-float-complex
[binary string]: https://docs.python.org/3/library/functions.html#bin
[`numpy.packbits`]: https://numpy.org/doc/stable/reference/generated/numpy.packbits.html
[`tobytes()`]: https://numpy.org/doc/stable/reference/generated/numpy.ndarray.tobytes.html#numpy.ndarray.tobytes
[`gmpy2`]: https://gmpy2.readthedocs.io/en/latest/intro.html
[`gmpy2.from_binary()`]: https://gmpy2.readthedocs.io/en/latest/overview.html#miscellaneous-gmpy2-functions
[Perfplot]: https://github.com/nschloe/perfplot




