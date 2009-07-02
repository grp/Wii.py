import Wii, sys

if(len(sys.argv) < 2):
	print "Usage: python tikinfo.py <ticket> ..."
	sys.exit(0)

for i in range(1, len(sys.argv)):
	elem = sys.argv[i]
	print Wii.Ticket().loadFile(elem)
	print "\n"
