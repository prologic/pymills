# Module:   misc
# Date:     04th August 2004
# Author:   James Mills <prologic@shortcircuit.net.au>

"""Miscellaneous

Various miscellaneous functions that don't fit
Use as documented.
"""

import time
import math


def hmsToSeconds(h=0, m=0, s=0):
    """hmsToSeconds(h=0, m=0, s=0) -> int

    Calculates the number of seconds,
    given hours (h), minutes (m) and
    seconds (s=0).

    Example::

        >>> hmsToSeconds(1)
        3600
        >>> hmsToSeconds(1, 24)
        5040
        >>> hmsToSeconds(1, 24, 54)
        5094
    """

    return h*3600 + m*60 + s


def getTotalTime(s, e):
    if e < s:
        return ((60*60*24) + e) - s
    else:
        return e - s


def addPercent(value, percentage):
    return float(value) * ((float(percentage) / 100.0) + 1.0)


def subPercent(value, percentage):
    return float(value) / ((float(percentage) / 100.0) + 1.0)


def bytes(bytes):
    if bytes >= 1024**4:
        return (round(bytes / float(1024**4), 2), "TB")
    elif bytes >= 1024**3:
        return (round(bytes / float(1024**3), 2), "GB")
    elif bytes >= 1024**2:
        return (round(bytes / float(1024**2), 2), "MB")
    elif bytes >= 1024**1:
        return (round(bytes / float(1024**1), 2), "KB")
    else:
        return bytes, "B"


def duration(seconds):
    days = int(seconds / 60 / 60 / 24)
    seconds = (seconds) % (60 * 60 * 24)
    hours = int((seconds / 60 / 60))
    seconds = (seconds) % (60 * 60)
    mins = int((seconds / 60))
    seconds = int((seconds) % (60))
    return (days, hours, mins, seconds)


def backMerge(l, n, t=" "):
    """Merge the last n items in list l joining with tokens t

    l - list
    n - merge last n items from l
    t - token (default: " ")
    """

    return l[:-n] + [t.join(l[-n:])]


def strToBool(s):
    return s.lower() in [
        "yes",
        "yeah",
        "1",
        "true",
        "ok",
        "okay",
        "k"]


def beat():
    from time import localtime, timezone
    x = localtime()

    y = (x[3] * 3600) + (x[4] * 60) + x[5]
    y += timezone + 3600

    if x[8] == 1:
        y -= 3600

    y = (y * 1000) / 86400.0

    if y > 1000:
        y -= 1000
    elif y < 0:
        y += 1000

    return y


def buildAverage(stime, x):

    ttime = time.time() - stime

    if ttime > 604800:
        xPerWeek = int(math.floor(
            float(x) / float((float(ttime) / float(604800))))
        )
    else:
        xPerWeek = 0

    if ttime > 86400:
        xPerDay = int(math.floor(
            float(x) / float((float(ttime) / float(86400))))
        )
    else:
        xPerDay = 0

    if ttime > 3600:
        xPerHour = int(math.floor(
            float(x) / float((float(ttime) / float(3600))))
        )
    else:
        xPerHour = 0

    if ttime > 60:
        xPerMinute = int(math.floor(
            float(x) / float((float(ttime) / float(60))))
        )
    else:
        xPerMinute = 0

    xPerSecond = int(math.floor(
        float(x) / float(ttime))
    )

    avg = ""
    if xPerWeek > 0:
        avg += "%d/w " % xPerWeek
    if xPerDay > 0:
        avg += "%d/d " % xPerDay
    if xPerHour > 0:
        avg += "%d/h " % xPerHour
    if xPerMinute > 0:
        avg += "%d/m " % xPerMinute
    if xPerSecond > 0:
        avg += "%d/s " % xPerSecond

    avg = avg.strip()
    if avg == "":
        avg = "~=0"

    return avg, x
