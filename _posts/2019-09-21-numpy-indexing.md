---
layout: post
title:  "Multi-dimensional Indexing in Numpy"
date:   2019-09-21 11:52:00 +0200
categories: python timing
---

[(This post is based on an answer of mine on StackOverflow)](https://stackoverflow.com/questions/57623010/optimizing-performance-of-list-comprehension-using-all-indexes-in-own-functions/57750084#57750084)

If you want to index an element in a multi-dimensional (i.e. nested) list in Python, you have to do this manually:

{% highlight python %}
nested_list = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9],
]
print(nested_list[1][1])
> 5
{% endhighlight %}

Already for this 2d example, it becomes ugly rather quickly. Numpy is a great python package for working with multi-dimensional numerical data. You can effectively use it the same as if it is still the same data-structure in Python.

{% highlight python %}
import numpy as np
nested_array = np.array([
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9],
])
print(nested_array[1][1])
> 5
{% endhighlight %}

However, Numpy also natively supports [tuple-indexing](https://docs.scipy.org/doc/numpy/reference/arrays.indexing.html):

{% highlight python %}
print(nested_array[(1, 1)])
> 5
print(nested_array[1, 1])
> 5
{% endhighlight %}

So... which is faster? To test, we create a large empty array and index four out of six dimensions:

{% highlight bash %}
$python --version
Python 3.6.3
    
$python -m timeit -s "import numpy as np; X = np.empty((9,9,9,9,9,9)); idx=(1,2,3,4)" "x = X[idx[0]][idx[1]][idx[2]][idx[3]]"
1000000 loops, best of 3: 0.644 usec per loop

$python -m timeit -s "import numpy as np; X = np.empty((9,9,9,9,9,9)); idx=(1,2,3,4)" "x = X[idx[0],idx[1],idx[2],idx[3]]"
1000000 loops, best of 3: 0.318 usec per loop
    
$python -m timeit -s "import numpy as np; X = np.empty((9,9,9,9,9,9)); i0, i1, i2, i3=(1,2,3,4)" "x = X[i0,i1,i2,i3]"
1000000 loops, best of 3: 0.221 usec per loop
    
$python -m timeit -s "import numpy as np; X = np.empty((9,9,9,9,9,9)); idx=(1,2,3,4)" "x = X[idx]"
10000000 loops, best of 3: 0.186 usec per loop
{% endhighlight %}

Conclusion: using tuple-indexing is significantly faster than nested indexing.
