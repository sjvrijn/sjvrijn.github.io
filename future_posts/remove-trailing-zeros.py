# coding: utf-8
#https://stackoverflow.com/questions/52908011/better-way-to-remove-trailing-zeros-from-an-integer

def remove_zeros_strip(n):
    return int(str(n).rstrip('0'))
    
def remove_zeros_while(n):
    while n % 10 == 0:
        n //= 10
    return n
    
get_ipython().run_line_magic('timeit', 'remove_zeros_strip(100)')
get_ipython().run_line_magic('timeit', 'remove_zeros_while(100)')
get_ipython().run_line_magic('timeit', 'remove_zeros_while(1_000)')
get_ipython().run_line_magic('timeit', 'remove_zeros_strip(1_000)')
get_ipython().run_line_magic('timeit', 'remove_zeros_strip(1_000_000)')
get_ipython().run_line_magic('timeit', 'remove_zeros_while(1_000_000)')
get_ipython().run_line_magic('timeit', 'remove_zeros_while(1_000_000_000)')
get_ipython().run_line_magic('timeit', 'remove_zeros_strip(1_000_000_000)')
