---
layout: post
title:  "Python's timeit: a How-To"
date:   2019-09-28 12:00:00 +0200
categories: python timing
---

As the main topic of this blog is going to be timing experiments in Python, let's start by having a look at the main tool I use to perform these experiments: Python's built-in [`timeit`][1] module.

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

1. Standalone one-liners  
  * `", ".join(str(n) for n in range(100))`
  * `", ".join([str(n) for n in range(100)])`
  * `", ".join(map(str, range(100)))`
2. Standalone multi-liners  
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
3. Either of the above with some setup required  
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
Python's `timeit` module can also be run as a commandline tool.

{% highlight bash %}
$ python -m timeit -n 10000 'pass'
10000 loops, best of 3: 0.0109 usec per loop
{% endhighlight %}

The usage is similar to the imported function as shown in the previous section, although the `-n` option is more optional than in the imported function. What I mean with that? If you don't specify a number of times to run your snippet, it will try successive powers of 10 (10, 100, 1000, ...) until the total time spent is at least 0.2 seconds. It also reports the actual time per iteration, instead of having to calculate that yourself. This is reported in `nsec`, `usec`, `msec` or `sec`, for nano-, micro-, mili- and whole seconds respectively.

{% highlight bash %}
$ python3 -m timeit 'pass'
100000000 loops, best of 3: 0.00856 usec per loop
{% endhighlight %}

### Standalone one-liners
Testing one-liners with the commandline is as easy as replacing `pass` from the introduction with the code you want to test, and the `timeit` tool will automatically report the time in a nice human-readable format.

{% highlight bash %}
$ python -m timeit '", ".join(str(n) for n in range(100))'
10000 loops, best of 3: 23.3 usec per loop
$ python -m timeit '", ".join([str(n) for n in range(100)])'
10000 loops, best of 3: 20 usec per loop
$ python -m timeit '", ".join(map(str, range(100)))'
100000 loops, best of 3: 16.4 usec per loop
{% endhighlight %}

### Standalone multi-liners
As before, the simplest way to test a snippet of multiple lines is to join the statements with a semicolon if no indentation is required. When indentation is required, the other option is to pass multiple strings as arguments to the command. Note that you still have to add the indentation properly yourself! This can get tricky to count if your indentation is more than a single level deep, but is usually not too hard.

{% highlight bash %}
$ python -m timeit 'x = []' 'for i in range(1000):' '    x.append(i)'
10000 loops, best of 3: 74.2 usec per loop

$ python -m timeit 'x = []' 'for i in range(1000):' '    x += [i]'
10000 loops, best of 3: 71.3 usec per loop
{% endhighlight %}


### Setup required
To add some initial setup such as imports or variable declarations, we can use the `-s` option:

{% highlight bash %}
$ python3 -m timeit -s 'pass' 'pass'
100000000 loops, best of 3: 0.00856 usec per loop
{% endhighlight %}

The setup *does* come before the statement to test in this case, so that makes it a bit more intuitive to read.

{% highlight bash %}
$ python -m timeit -s 'text = "sample string"; char = "g"' 'char in text'
10000000 loops, best of 3: 0.0335 usec per loop
$ python -m timeit -s 'text = "sample string"; char = "g"' 'text.find(char)'
10000000 loops, best of 3: 0.147 usec per loop
{% endhighlight %}

## IPython/Jupyter magics: %timeit
When working in the [IPython][2] interactive shell, or in a [Jupyter notebook][3] with the IPython kernel, you have access to the so-called ['magic commands'][4]. For timeit, there is the [`%timeit`][5] magic. It simply takes the code you type after it and runs the `timeit` command on it! Like magic!

One small caveat is that the outcome is reported as a mean +/- standard deviation of multiple repetitions, while the original Python documentation suggests always using the minimum.

### Standalone one-liners
For simple one-liners, just type the code as you would normally, and type `%timeit` before it. That's all!

```python
%timeit ", ".join(str(n) for n in range(100))
```
24.1 µs ± 314 ns per loop (mean ± std. dev. of 7 runs, 10000 loops each)
```python
%timeit ", ".join([str(n) for n in range(100)])
```
20.4 µs ± 266 ns per loop (mean ± std. dev. of 7 runs, 10000 loops each)
```python
%timeit ", ".join(map(str, range(100)))
```
18.2 µs ± 777 ns per loop (mean ± std. dev. of 7 runs, 100000 loops each)

### Standalone multi-liners
The `%timeit` magic doesn't quite work for multi-line snippets though. Why? Because magics with a *single* `%` are *line-magics*. For *cell-magics*, you just have to add another `%` to make it `%%timeit`. Then it will time all the code in your cell. No further difficulties whatsoever! 

```python
%%timeit
x = []
for i in range(1000):
    x.append(i)
```
75.1 µs ± 39.8 ns per loop (mean ± std. dev. of 7 runs, 10000 loops each)

```python
%%timeit
x = []
for i in range(1000):
    x += [i]
```
72.4 µs ± 2.33 µs per loop (mean ± std. dev. of 7 runs, 10000 loops each)

### Setup required
Now you might be thinking "but if this `%timeit` just takes your code and times it, where do I put my setup command?" The answer: just run it in some previous cell! As IPython already takes care of passing your code on to the `timeit` module properly, it also automatically passes along all current global variables. So we can simply first run a cell with our setup:

```python
text = "sample string"
char = "g"
```

And use the simple `%timeit` magic to time the code we are actually interested in, without specifying which setup is associated with it.

```python
%timeit char in text
```
49.9 ns ± 1.09 ns per loop (mean ± std. dev. of 7 runs, 10000000 loops each)
```python
%timeit text.find(char)
```
178 ns ± 24.6 ns per loop (mean ± std. dev. of 7 runs, 10000000 loops each)

## Summary
I hope to have shown in this article how you can easily use Python's `timeit` module to measure execution times of your snippets, whether for fun or profit. Although each has it's pros and cons (see below), I will personally recommend to use IPython's `(%)%timeit` magics as they are the most intuitive to use: just write the code as you would normally with the `%timeit` magic in front.

### Pros and Cons
- `from timeit import timeit`
  - Pros:
	+ Time taken returned within Python process, so can easily be used in further processing 
  - Cons:
    - Must specify number of iterations manually
	- Must manually calculate amount of time spent per iteration
- `python -m timeit`
  - Pros:
	+ Gives nice and clear output
  - Cons:
    - Multi-line snippets are less intuitive
    - Commandline can be 'scary' to some
- `(%)%timeit`
  - Pros:
	+ Easiest to use
	+ Setup is dealt with automatically
  - Cons:
    - Needs Ipython and/or Jupyter installed
	- Gives mean +/- standard deviation as result, when Python documentation suggests looking at the minimum


[1]: https://docs.python.org/3/library/timeit.html
[2]: https://pypi.org/project/ipython/
[3]: https://jupyter.org/
[4]: https://ipython.readthedocs.io/en/stable/interactive/magics.html
[5]: https://ipython.readthedocs.io/en/stable/interactive/magics.html#magic-timeit
