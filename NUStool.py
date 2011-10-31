#----------------------------------------------------------------------
# NUS - a simple command line tool for NUS downloading.
# (c) 2009 |Omega| and #HACKERCHANNEL Productions.
#
# Wii.py (c) Xuzz, SquidMan, megazig, TheLemonMan, |Omega|, and Matt_P.
#----------------------------------------------------------------------

import Wii, sys, os, shutil

def downloadPack(titleid, version, outDir, pack):
	print "downloadPack(0x%016x, %d, %s, %d)" % (titleid,version,outDir,pack)
	if version != 0:
		print "downloading....",
		Wii.NUS.download(titleid, version).dumpDir(outDir)
	else:
		print "downloading....",
		Wii.NUS.download(titleid).dumpDir(outDir)
	print "done"
	if pack == True:
		print "packing........",
		Wii.WAD.loadDir(outDir).dumpFile(str(outDir+".wad"))
		shutil.rmtree(outDir)
		print "done"

if len(sys.argv) % 3 == 2:
	pack, x = False, 1
else:
	pack, x = True, 0

for i in range(1 + x, len(sys.argv), 3):
	titleid = int(sys.argv[i], 16)
	print "TitleId: %016x" % titleid
	version = int(sys.argv[i+1])
	print "Version: %d" % version
	outDir = sys.argv[i+2]
	downloadPack(titleid, version, outDir, pack)

