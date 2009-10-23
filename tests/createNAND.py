#!/usr/bin/python

import os, Wii

nand = Wii.NAND('/home/megazig/Wii.py/nand')

# change for region
sysV = 417
iosV = 6174

#Wii.NUS.download(0x0000000100000002, sysV).dumpDir("0000000100000002")
#Wii.NUS.download(0x000000010000003C, iosV).dumpDir("000000010000003C")
#Wii.NUS.download(0x0001000848414C45).dumpDir("0001000848414C45")
#Wii.NUS.download(0x0001000848414B45).dumpDir("0001000848414B45")

nand.importTitle(Wii.NUS.download(0x0000000100000002, sysV), False)
nand.importTitle(Wii.NUS.download(0x000000010000003C, iosV), False)
nand.importTitle(Wii.NUS.download(0x0001000848414C45), False)
nand.importTitle(Wii.NUS.download(0x0001000848414B45), False)
