
from random import seed, random

from pymills.ann import *
from pymills.event import *

class OutputNode(Node):

	def __init__(self, event, output):
		Node.__init__(self, event)

		self._output = output

	@listener("signal")
	def onSIGNAL(self, source, level):
		print self._output

def new_output(*args, **kwargs):
	class NewOutputNode(OutputNode):
		pass
	return NewOutputNode(*args, **kwargs)

event = EventManager()

i1 = new_node(event)
i2 = new_node(event)

n1 = new_neuron(event, 2.0)

o1 = new_output(event, "foo")

s1 = new_synapse(event, 2.0)
s2 = new_synapse(event, 3.0)

i1.link(s1)
i2.link(s2)

s1.link(n1)
s2.link(n1)

n1.link(o1)
n1.link(n1)

seed()

while True:
	try:
		event.flush()
		sleep(random())
		i1.fire()
		sleep(random())
		i2.fire()
		print "..."
		s1._weight = random()
		s2._weight = random()
		n1._threshold = random()
	except FilteredEvent:
		pass
	except KeyboardInterrupt:
		break

i1.stop()
i2.stop()
n1.stop()
s1.stop()
s2.stop()
o1.stop()
