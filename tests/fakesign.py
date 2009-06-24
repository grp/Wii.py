from disc import *
from title import *
from Struct import Struct
import os

def fakesignPartition(self, iso, index)
	iso = WOD(iso)
	iso.openPartition(index)
	fstBuf = iso.getFst()	"
	fn = open(os.getcwd() + "/" + iso.discHdr.discId + iso.discHdr.gameCode + iso.discHdr.region + "/" + "PART" + index + "/" + 'appldr.bin', 'w+b')
	fn.write(iso.getPartitionApploader()) #saved to cwd/GAMEID/PARTITION/file
	fn.close()
	fn = open(os.getcwd() + "/" + iso.discHdr.discId + iso.discHdr.gameCode + iso.discHdr.region + "/" + "PART" + index + "/" + 'h3.bin', 'w+b')
	fn.write(iso.getPartitionH3Table())
	fn.close()
	fn = open(os.getcwd() + "/" + iso.discHdr.discId + iso.discHdr.gameCode + iso.discHdr.region + "/" + "PART" + index + "/" + 'main.dol', 'w+b')
	fn.write(iso.getPartitionMainDol())
	fn.close()
	fn = open(os.getcwd() + "/" + iso.discHdr.discId + iso.discHdr.gameCode + iso.discHdr.region + "/" + "PART" + index + "/" + 'fst.bin', 'w+b')
	fn.write(fstBuf)
	fn.close()
	fileNumber = struct.unpack(">I", fstBuf[0x8:0xc])[0]
	fileObject = iso.fstObject("", iso)
	iso.parseFst(fstBuf, fstBuf[12 * fileNumber:], 0, fileObject)
	fileObject.write(os.getcwd() + "/" + iso.discHdr.discId + iso.discHdr.gameCode + iso.discHdr.region + "/" + "PART" + index + "/")
	fileObject.close()
	isoTik = Ticket(iso.getPartitionTik())
	isoTik.dump(os.getcwd() + "/" + iso.discHdr.discId + iso.discHdr.gameCode + iso.discHdr.region + "/" + "PART" + index + "/" + "tik")
	isoTMD = TMD(iso.getPartitionTmd())
	isoTMD.dump(os.getcwd() + "/" + iso.discHdr.discId + iso.discHdr.gameCode + iso.discHdr.region + "/" + "PART" + index + "/" + "tmd")
