#!/usr/bin/python

import sys
from formats import locDat

def main():
	if len(sys.argv) == 1:
		print 'Usage: python testLOC.py <filename.dat>'
		sys.exit(1)

	sdLoc = locDat(sys.argv[1])

	print '%s' % sdLoc

	#concorsiMii = sdLoc.getTitle(0, 0, 0)
	sdLoc.delTitle(0, 0, 0)

if __name__ == "__main__":
	main()
