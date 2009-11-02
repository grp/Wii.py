#----------------------------------------------------------------------
# NUS - a simple command line tool for NUS downloading.
# (c) 2009 |Omega| and #HACKERCHANNEL Productions.
#
# Wii.py (c) Xuzz, SquidMan, megazig, TheLemonMan, |Omega|, and Matt_P.
#----------------------------------------------------------------------

import Wii, sys, os, shutil

def downloadPack(titleid, version, outDir, pack):
	if version != 0:
		Wii.NUS.download(titleid, version).dumpDir(outDir)
	else:
		Wii.NUS.download(titleid).dumpDir(outDir)
	if pack == True:
		Wii.WAD.loadDir(outDir).dumpFile(str(outDir+".wad"))
		shutil.rmtree(outDir)

if len(sys.argv) % 3 == 2:
	pack, x = False, 1
else:
	pack, x = True, 0

for i in range(1 + x, len(sys.argv), 3):
	titleid = int(sys.argv[i], 16)
	version = int(sys.argv[i+1])
	outDir = sys.argv[i+2]
	downloadPack(titleid, version, outDir, pack)