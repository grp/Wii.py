#!/usr/bin/python

import sys, Wii

def main():
	if len(sys.argv) == 1:
		print 'Usage: python testSAVE.py <filename.bin>'
		sys.exit(1)

	save = Savegame(sys.argv[1])
	save.analyzeHeader()
	print '%s' % save
	save.getBanner()
	for i in range(save.getIconsCount()):
		save.getIcon(i)
	save.extractFiles()
	sys.exit(0)

if __name__ == "__main__":
	main()
