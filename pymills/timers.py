from warnings import warn

warn(DeprecationWarning("pymills.timers is deprecated. Use pymills.event.timers"))

from pymills.event.timers import *
