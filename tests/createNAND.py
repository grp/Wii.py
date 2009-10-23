#!/usr/bin/python

import os, sys, Wii

def lolcrypt( string ):
	key = 0x73b5dbfa
	out = ""
	#while(*string)
	for x in xrange(len(string)):
		if ord(string[x]) == '\0':
			continue
		#*string ^= (key & 0xff)
		out = out + chr( ord(string[x]) ^ (key & 0xff) )
		#string += 1
		#key = ((key<<1) | (key>>31))
		key = ((key & 0x8fffffff) << 1) | ((key & 0xfffffffe) >> 1)
	for x in xrange( 0x100 - len(out) ):
		out = out + '\0'
	return out

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
	#nand.importTitle(Wii.NUS.download(0x0001000848414C45), False)
	#nand.importTitle(Wii.NUS.download(0x0001000848414B45), False)
	settings = "AREA=USA\r\nMODEL=RVL-001(USA)\r\nDVD=0\r\nMPCH=0x7FFE\r\nCODE=LU\r\nSERNO=56866191\r\nVIDEO=NTSC\r\nGAME=US\r\n"
	file = open(sys.argv[1] + '/title/00000001/00000002/data/setting.txt', 'wb')
	file.write(lolcrypt(settings))
	file.close()
	print lolcrypt(lolcrypt(settings))
	settings_txt = Wii.CONF(sys.argv[1] + '/title/00000001/00000002/data/setting.txt')
	print settings_txt.getKeysName()
	#nand.add('setting.txt')
	sys.exit(0)

if __name__ == "__main__":
	main()

