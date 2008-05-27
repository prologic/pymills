from pymills.threadpool import Pool, threaded, threadpool

from time import sleep
from random import random

pool = Pool(3)

@threadpool(pool)
def test_threadpool(i):
	print 'threadpool %i enter' % i
	sleep(random())
	print 'threadpool %i exit' % i

print 'threadpool example'
for i in range(6):
	test_threadpool(i)
pool.join()
print 'done'
print ''

@threaded
def test_threaded(i):
	print 'threaded %i enter' % i
	sleep(random())
	print 'threaded %i exit' % i

print 'threaded example'
for i in range(5):
	test_threaded(i)
print 'done'
