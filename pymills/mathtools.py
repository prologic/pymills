# Module:	mathtools
# Date:		27th January 2011
# Author:	James Mills, prologic at shortcircuit dot net au

"""Math Tools

Module of small useful math tools aka common math routines.
"""

from math import sqrt

def mean(xs):
    """Calculate the mean of a list of numbers given by xs"""

    return sum(xs) / len(xs)

def std(xs):
    """Calculate the standard deviation of a list of numbers give by xs"""

    m = mean(xs)
    dxs = (x - m for x in xs)
    qdxs = (x * x for x in dxs)
    s = l = 0
    for i in qdxs:
        s += i
        l += 1
    return sqrt(s / (l - 1))
