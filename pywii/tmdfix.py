import Wii, sys

if(len(sys.argv) < 2):
	print "Usage: python tmdfix.py <tmd> ..."
	sys.exit(0)

for i in range(1, len(sys.argv)):
	elem = sys.argv[i]
	Wii.TMD().loadFile(elem).dump(elem)
