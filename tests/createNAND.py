#!/usr/bin/python

import os, sys, Wii

def lolcrypt( string ):
	key = 0x73B5DBFA
	out = ''
	for x in xrange(len(string)):
		out += chr( ord(string[x]) ^ (key & 0xff) )
		key = ((key << 1) & 0xffffffff) | ((key >> 31) & 0xffffffff)
	out += ( '\x00' * ( 0x100 - len(out) ) )
	return out

def main():
	if len(sys.argv) == 1:
		print 'Usage: python createNAND.py <foldername>'
		sys.exit(1)

	nand = Wii.NAND(sys.argv[1])

	# change for region
	sysV = 417
	iosV = 6174

	# IOS60 and 4.0U
	nand.importTitle(Wii.NUS.download(0x0000000100000002, sysV), False, False, False)
	nand.importTitle(Wii.NUS.download(0x000000010000003C, iosV), False, False, False)
	# IOS61 and Shop
	nand.importTitle(Wii.NUS.download(0x000000010000003D), False, False, False)
	nand.importTitle(Wii.NUS.download(0x0001000248414641), False, False, False)
	# EULA and RegnSel
	#nand.importTitle(Wii.NUS.download(0x0001000848414C45), False, False, True, False)
	#nand.importTitle(Wii.NUS.download(0x0001000848414B45), False, False, True, False)
	# setting.txt
	settings = "AREA=USA\r\nMODEL=RVL-001(USA)\r\nDVD=0\r\nMPCH=0x7FFE\r\nCODE=LU\r\n\nSERNO=568661910\r\nVIDEO=NTSC\r\nGAME=US\r\n"
	#settings = "CODE=LU\r\nAREA=EUR\r\nDVD=0\r\nGAME=EU\r\nVIDEO=PAL\r\nMPCH=0x7FFE\r\nMODEL=RVL-001(EUR)\r\nSERNO=-559038737\r\n"
	file = open(sys.argv[1] + '/title/00000001/00000002/data/setting.txt', 'wb')
	file.write(lolcrypt(settings))
	file.close()
	#print lolcrypt(lolcrypt(settings))
	settings_txt = Wii.CONF(sys.argv[1] + '/title/00000001/00000002/data/setting.txt')
	#print settings_txt.getKeysName()
	#for x in settings_txt.getKeysName():
	#	print settings_txt.getKeyValue(x)
	#nand.add('setting.txt')
	sys.exit(0)

if __name__ == "__main__":
	main()

