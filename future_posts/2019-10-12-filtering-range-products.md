---
layout: post
title:  "Filtering elements from a product of ranges"
date:   2019-10-12 12:00:00 +0200
categories: python timing
---


```
In [1]: from itertools import product

In [2]: %timeit list(filter(lambda x: x[0] > x[1], product(range(10), range(10))))
15.3 µs ± 256 ns per loop (mean ± std. dev. of 7 runs, 100000 loops each)

In [3]: %timeit [(a, b) for (a, b) in product(range(10), range(10)) if a>b]
8.76 µs ± 2.32 µs per loop (mean ± std. dev. of 7 runs, 100000 loops each)
```



```
In [4]: %timeit list(filter(lambda x: x[0] > x[1], product(range(50), range(100))))
691 µs ± 63.4 µs per loop (mean ± std. dev. of 7 runs, 1000 loops each)

In [5]: %timeit [(a, b) for (a, b) in product(range(50), range(100)) if a > b]
247 µs ± 21.4 µs per loop (mean ± std. dev. of 7 runs, 1000 loops each)
```



```
In [6]: %timeit [xyz for xyz in product(range(10), range(10), range(50)) if xyz[0] > xyz[1]]
481 µs ± 1.26 µs per loop (mean ± std. dev. of 7 runs, 1000 loops each)

In [7]: %timeit [(x, y, z) for x, y, z in product(range(10), range(10), range(50)) if x > y]
343 µs ± 21 µs per loop (mean ± std. dev. of 7 runs, 1000 loops each)
```



```
In [8]: %timeit [xyz for xyz in product(range(50), range(100), range(50)) if xyz[0] > xyz[1]]
23.6 ms ± 320 µs per loop (mean ± std. dev. of 7 runs, 10 loops each)

In [9]: %timeit [(x, y, z) for x, y, z in product(range(50), range(100), range(50)) if x > y]
17.1 ms ± 2.89 ms per loop (mean ± std. dev. of 7 runs, 100 loops each)
```


