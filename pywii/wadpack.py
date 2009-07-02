import Wii, sys

if(len(sys.argv) < 3):
	print "Usage: python wadpack.py <input> <output> ..."
	sys.exit(0)

for i in range(1, len(sys.argv), 2):
	elem = sys.argv[i]
	elem2 = sys.argv[i + 1]
	Wii.WAD(elem).pack(elem2)
