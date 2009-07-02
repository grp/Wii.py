import Wii, sys

if(len(sys.argv) < 2):
	print "Usage: python tmdinfo.py <tmd> ..."
	sys.exit(0)

for i in range(1, len(sys.argv)):
	elem = sys.argv[i]
	print Wii.TMD().loadFile(elem)
	print "\n"
