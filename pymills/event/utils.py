# Module:	utils
# Date:		27th August 2008
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Utils

Utility Functions
"""

from threading import enumerate as threads

def workers():
	"""workers() -> list of workers

	Get the current list of active Worker's
	"""

	return [thread for thread in threads() if isinstance(thread, Worker)]
