#!/usr/bin/python

import os, sys
from U8 import *
from title import WAD

def main():
	if len(sys.argv) != 3:
		print 'Usage: python sysmenuUnpack.py <filename.wad> <output_folder>'
		sys.exit(1)

	sysmenuWad = WAD(sys.argv[1])
	sysmenuWad.unpack(sys.argv[2])

	for file in os.listdir(sys.argv[2]):
		if open(sys.argv[2] + file).read(4) == '\x55\xaa\x38\x2d':
			U8(sys.argv[2] + file).unpack(sys.argv[2] + file + '_decompressed/') 
	
if __name__ == "__main__":
	main()
