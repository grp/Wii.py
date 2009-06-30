import os
from U8 import *
from title import WAD

sysmenuWad = WAD('/home/giuseppe/Scrivania/RVL-WiiSystemmenu-v258.wad')
sysmenuWad.unpack('/home/giuseppe/Scrivania/sysdump')

for file in os.listdir('/home/giuseppe/Scrivania/sysdump'):
	if open('/home/giuseppe/Scrivania/sysdump/' + file).read(4) == '\x55\xaa\x38\x2d':
		U8('/home/giuseppe/Scrivania/sysdump/' + file).unpack('/home/giuseppe/Scrivania/sysdump/' + file + '_decompressed/') 
