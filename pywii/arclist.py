import Wii, sys

if(len(sys.argv) < 2):
	print "Usage: python arclist.py <arcfile> ..."
	sys.exit(0)

for i in range(1, len(sys.argv)):
	elem = sys.argv[i]
	print "Listing of %s:" % elem
	print Wii.U8(elem)
	print "\n"
