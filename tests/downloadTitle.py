#!/usr/bin/python

import os, sys, Wii

def main():
	if len(sys.argv) == 1:
		print 'Usage: python downloadTitle.py <titleid> <version>'
		sys.exit(1)

	titleid = sys.argv[1]
	titlehex = int(titleid, 16)
	version = sys.argv[2]

	Wii.NUS.download(titlehex, int(version)).dumpDir(titleid + '.' + version)

	sys.exit(0)

if __name__ == "__main__":
	main()


