#!/usr/bin/env python

from time import sleep
from random import seed, random

from pymills.ann import new_node, new_connection, \
		new_neuron, Output
from pymills.event import Manager

class MyOutput(Output):

	def do(self):
		print "Oh Yeah!"

event = Manager()

i1 = new_node(event)
i2 = new_node(event)

n1 = new_neuron(event, 2.0)

o1 = MyOutput()

s1 = new_connection(event, 2.0)
s2 = new_connection(event, 3.0)
#s3 = new_connection(event, 5.0)

i1.link(s1)
i2.link(s2)

s1.link(n1)
s2.link(n1)

n1.link(o1)
#n1.link(s3)
#s3.link(n1)

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
	except KeyboardInterrupt:
		break

i1.stop()
i2.stop()
n1.stop()
s1.stop()
s2.stop()
#s3.stop()
o1.stop()