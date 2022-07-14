---
layout: post
title:  "Filtering elements from a list of tuples"
date:   2019-10-16 07:00:00 +0200
tags: python timing
---

Recently I was writing some code to fill a 50 by 100 by 50 3D matrix with some calculated values, but only at the indices that passed a certain check: the first index has to be smaller than the second. The naive way to do this would be a nested for-loop with a `continue` if the check was not passed.

```python
for a in range(x):
    for b in range(y):
        for c in range(z):
            if a <= b:
                continue

            matrix[a, b, c] = ...
```

This solution however, is a) long and b) less re-usable. Instead, I wanted to create the list of index-tuples beforehand, preferably using [`itertools.product`][1] to make the code cleaner. Simply put:

```python
from itertools import product

indices = []
for a, b, c in product(range(x), range(y), range(z)):
    if a > b:
        indices.append((a, b, c))
```

which we can easily rewrite as a one-liner in Python. For this we have two options: using the built-in [`filter`][2] function with a [`lambda`][3], or by using a [list-comprehension][4].

So, which is faster? To test, we'll just leave out the third index we're not using for the check:

```
%timeit list(filter(lambda x: x[0] > x[1], product(range(10), range(10))))
```
15.3 µs ± 256 ns per loop (mean ± std. dev. of 7 runs, 100000 loops each)
```
%timeit [(a, b) for (a, b) in product(range(10), range(10)) if a>b]
```
8.76 µs ± 2.32 µs per loop (mean ± std. dev. of 7 runs, 100000 loops each)

In this small 10x10 example, the list-comprehension is almost twice as fast. What happens if we increase the ranges to the sizes we are actually using?

```
%timeit list(filter(lambda x: x[0] > x[1], product(range(50), range(100))))
```
691 µs ± 63.4 µs per loop (mean ± std. dev. of 7 runs, 1000 loops each)
```
%timeit [(a, b) for (a, b) in product(range(50), range(100)) if a > b]
```
247 µs ± 21.4 µs per loop (mean ± std. dev. of 7 runs, 1000 loops each)

The list-comprehension is now more than twice as fast as the `filter(lambda x: ...)` combination! This does make some sense as list-comprehensions are considered more 'pythonic' for a while now, and have received a bit more love in terms of performance improvements.

This comparison still leaves room for improvement in two aspects:
1. We're not considering the 3rd index yet
2. We're comparing two across methods of accessing the values for `a` and `b`: by index and by tuple unpacking

As the `filter(function, iterable)` built-in only ever passes a single argument at a time to its `function`, we can't use it to compare these two accessing methods. Because we already know it's a lot slower too, we can just ignore it from now on.

So let's add that third index and compare the two value accessing methods in a list-comprehension:

```
%timeit [xyz for xyz in product(range(10), range(10), range(50)) if xyz[0] > xyz[1]]
```
481 µs ± 1.26 µs per loop (mean ± std. dev. of 7 runs, 1000 loops each)
```
%timeit [(x, y, z) for x, y, z in product(range(10), range(10), range(50)) if x > y]
```
343 µs ± 21 µs per loop (mean ± std. dev. of 7 runs, 1000 loops each)

The tuple unpacking seems to be about a quarter faster than the indexing method. Does this difference hold up if we increase the ranges in the first two indices?

```
%timeit [xyz for xyz in product(range(50), range(100), range(50)) if xyz[0] > xyz[1]]
```
23.6 ms ± 320 µs per loop (mean ± std. dev. of 7 runs, 10 loops each)
```
%timeit [(x, y, z) for x, y, z in product(range(50), range(100), range(50)) if x > y]
```
17.1 ms ± 2.89 ms per loop (mean ± std. dev. of 7 runs, 100 loops each)

*(Don't pay too much attention to the large difference in std. dev. for the two comparisons, as one only did 10 loops while the other did 100.)*

So interestingly, it seems like unpacking and re-packing a tuple is faster to access two of its values than just accessing those values by index without unpacking! Although this results in code that is slightly longer, I do think it's more readable, so I'm happy this turns out to be the (slightly) faster way :)

For a deeper understanding of what's going on here, we should probably look into the actual interpreted instructions using e.g. the disassembly module [`dis`][5]. To be continued...?


[1]: https://docs.python.org/3/library/itertools.html#itertools.product
[2]: https://docs.python.org/3/library/functions.html#filter
[3]: https://docs.python.org/3/tutorial/controlflow.html?highlight=lambda#lambda-expressions
[4]: https://docs.python.org/3/tutorial/datastructures.html?highlight=comprehensions#list-comprehensions
[5]: https://docs.python.org/3/library/dis.html?highlight=dis#module-dis
