import Wii, sys

if(len(sys.argv) < 2):
	print "Usage: python saveinfo.py <savegame> ..."
	sys.exit(0)

for i in range(1, len(sys.argv)):
	elem = sys.argv[i]
	print Wii.Savegame(elem)
	print "\n"
