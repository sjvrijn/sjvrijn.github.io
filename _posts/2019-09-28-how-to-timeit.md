---
layout: post
title:  "Python's timeit: a How-To"
date:   2019-09-28 12:00:00 +0200
categories: python timing
---

As the main topic of this blog is going to be timing experiments in Python, let's start by having a look at the main tool I use to perform these experiments: Python's built-in [`timeit`](https://docs.python.org/3/library/timeit.html) module.

In this post I will give a short and minimal introduction of the `timeit` module, and go over the three main ways to use it to time small snippets of Python code.

**Content**
* This line is replaced by the Table of Contents (so do not remove)
{:toc}

## Timey Wimey Python: timeit
What is Python's `timeit` module?

> This module provides a simple way to time small bits of Python code.
> It has both a Command-Line Interface as well as a callable one. It 
> avoids a number of common traps for measuring execution times.
> 
> -- timeit documentation

In contrast to profiling the runtime of your entire program, the `timeit` module is better suited to time small snippets. We can divide these comparisons in three classes, as illustrated by the examples I will use throuhgout this blogpost.

1. Standalone one-liners\
  * `", ".join(str(n) for n in range(100))`
  * `", ".join([str(n) for n in range(100)])`
  * `", ".join(map(str, range(100)))`
2. Standalone multi-liners\
  * 
  ```
  x = []
  for i in range(1000):
      x.append(i)
  ```
  * 
  ```
  x = []
  for i in range(1000):
      x += [i]
  ```
*(ignoring for the sake of example that the list-comprehension `[i for i in range(1000)]` is twice as fast)*
3. Either of the above with some setup required\
**Setup** `text = "sample string"; char = "g"`
  * `char in text`
  * `text.find(char)`

## In a script: import timeit
As `timeit` is a Python module, you can import it and write Python scripts for your tests. This method is the most self-documenting and repeatable way of writing your timing experiments, and makes it easy to store the results for further processing.

Before we can run any experiments, we need to import the relevant function:
{% highlight python %}
from timeit import timeit
{% endhighlight %}

The function has the following specification:
{% highlight python %}
time_spent = timeit(stmt='pass', number=1_000_000)
{% endhighlight %}

By running `timeit()` without any further arguments, we execute the default statement `stmt='pass'` a million times, showing the minimal overhead of Python's `pass` statement. 
{% highlight python %}
>>> timeit()
0.0090144
{% endhighlight %}

Unless specified otherwise, `timeit()` will always run the default of one million iterations. This also means you have to pick a useful number yourself to make it finish in a reasonable amount of time that's not too long or too short. The returned value is the number of seconds (as a `float`) it has taken to run the statement `number` times.

### Standalone one-liners
Let's start with comparing the simple one-liners. We give the statement we want to time as a string, and specify a custom number of iterations. Note that when your statement already deals with double-quoted strings, the whole string should be given single-quoted, or vice-versa.

{% highlight python %}
>>> from timeit import timeit
>>> timeit('", ".join(str(n) for n in range(100))', number=10_000)
0.3343242
>>> timeit('", ".join([str(n) for n in range(100)])', number=10_000)
0.2085556
>>> timeit('", ".join(map(str, range(100)))', number=10_000)
0.1828172
{% endhighlight %}

From the given `number` and returned time in seconds, we can calculate that each of these lines took **33.4**, **20.9** and **18.3** microseconds to execute respectively.

### Standalone multi-liners
Sometimes the snippet you want to test will consist of multiple statements. Python allows you to put multiple statements on a single line with a semicolon `x = 1; y = 2`. Then you can simply run your test as explained above for the standalone one-liners. This does not work for snippets with indented code like `if` or `for` though.

To time these snippets that *have* to span multiple lines, you can simply give `timeit()` a multi-line string as argument. The beautiful and Pythonic way to do this is using Python's multi-line strings. (The non-Pythonic way is to add `\n` characters in your regular strings.)

{% highlight python %}
>>> from timeit import timeit
>>> timeit('''x = []
... for i in range(1000):
...     x.append(i)''', number=10_000)
0.7762808
>>> timeit("""x = []
... for i in range(1000):
...     x += [i]""", number=10_000)
0.7307259
{% endhighlight %}


### Setup required
If there is some setup that only has to be run once, including it in a multi-line snippet means it's executed at every iteration. Then you'd be measuring something you don't want to measure! Instead, you can pass this setup statement as a separate argument to `timeit()`:

{% highlight python %}
time_spent = timeit(stmt='pass', setup='pass', number=1_000_000)
{% endhighlight %}

Setup snippets most commonly consist of non-indented code, so you can usually just use semicolons to join those statements in a regular string. Remember that the `stmt` argument comes *before* the `setup` argument if you don't pass them as keyword-arguments, even though the setup would normally be first.

{% highlight python %}
>>> from timeit import timeit
>>> timeit(stmt='char in text',
...        setup='text = "sample string"; char = "g"',
...        number=1_000_000)
0.0358061
>>> timeit('text.find(char)',
...        'text = "sample string"; char = "g"',
...        number=1_000_000)
0.1525827
{% endhighlight %}

## Commandline: python -m timeit

### Standalone one-liners

{% highlight bash %}
$ python -m timeit '", ".join(str(n) for n in range(100))'
10000 loops, best of 3: 23.3 usec per loop
$ python -m timeit '", ".join([str(n) for n in range(100)])'
10000 loops, best of 3: 20 usec per loop
$ python -m timeit '", ".join(map(str, range(100)))'
100000 loops, best of 3: 16.4 usec per loop
{% endhighlight %}

### Standalone multi-liners

{% highlight bash %}
$ python -m timeit 'x = []' 'for i in range(1000):' '    x.append(i)'
10000 loops, best of 3: 74.2 usec per loop

$ python -m timeit 'x = []' 'for i in range(1000):' '    x += [i]'
10000 loops, best of 3: 71.3 usec per loop
{% endhighlight %}


### Setup required

{% highlight bash %}
$ python -m timeit -s 'text = "sample string"; char = "g"' 'char in text'
10000000 loops, best of 3: 0.0335 usec per loop
$ python -m timeit -s 'text = "sample string"; char = "g"' 'text.find(char)'
10000000 loops, best of 3: 0.147 usec per loop
{% endhighlight %}

## IPython magic command: %timeit

### Standalone one-liners

```
In [1]: %timeit ", ".join(str(n) for n in range(100))
24.1 µs ± 314 ns per loop (mean ± std. dev. of 7 runs, 10000 loops each)

In [2]: %timeit ", ".join([str(n) for n in range(100)])
20.4 µs ± 266 ns per loop (mean ± std. dev. of 7 runs, 10000 loops each)

In [3]: %timeit ", ".join(map(str, range(100)))
18.2 µs ± 777 ns per loop (mean ± std. dev. of 7 runs, 100000 loops each)
```

### Standalone multi-liners

```
In [1]: %%timeit
    ..: x = []
    ..: for i in range(1000):
    ..:     x.append(i)
    ..:
75.1 µs ± 39.8 ns per loop (mean ± std. dev. of 7 runs, 10000 loops each)

In [2]: %%timeit
    ..: x = []
    ..: for i in range(1000):
    ..:     x += [i]
    ..:
72.4 µs ± 2.33 µs per loop (mean ± std. dev. of 7 runs, 10000 loops each)
```

### Setup required

```
In [1]: text = "sample string"
In [2]: char = "g"

In [3]: %timeit char in text
49.9 ns ± 1.09 ns per loop (mean ± std. dev. of 7 runs, 10000000 loops each)

In [4]: %timeit text.find(char)
178 ns ± 24.6 ns per loop (mean ± std. dev. of 7 runs, 10000000 loops each)
```
