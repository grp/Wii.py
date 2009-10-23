#!/usr/bin/python

import os, sys, Wii

def main():
	if len(sys.argv) == 1:
		print 'Usage: python createNAND.py <foldername>'
		sys.exit(1)

	nand = Wii.NAND(sys.argv[1])

	# change for region
	sysV = 417
	iosV = 6174

	nand.importTitle(Wii.NUS.download(0x0000000100000002, sysV), False)
	nand.importTitle(Wii.NUS.download(0x000000010000003C, iosV), False)
	nand.importTitle(Wii.NUS.download(0x0001000848414C45), False)
	nand.importTitle(Wii.NUS.download(0x0001000848414B45), False)
	sys.exit(0)

if __name__ == "__main__":
	main()

