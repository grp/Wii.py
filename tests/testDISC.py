from disc import *
from title import *
from Struct import Struct
import os

iso = WOD('/enter/other/wii/SUPER_MARIO_GALAXY.iso')
iso.openPartition(1)
#print '%s' % iso
#iso.decryptAll()
#open('appldr.bin', 'w+b').write(iso.getPartitionApploader())
#open('appldr.bin', 'w+b').close()
fstBuf = iso.getFst()
open('fst.bin', 'w+b').write(fstBuf)
open('fst.bin', 'w+b').close()

fileNumber = struct.unpack(">I", fstBuf[0x8:0xc])[0]
fileObject = iso.fstObject("", iso)
iso.parseFst(fstBuf, fstBuf[12 * fileNumber:], 0, fileObject)
print fileObject.getList()
fileObject.write(os.getcwd() + "/" + iso.discHdr.discId + iso.discHdr.gameCode + iso.discHdr.region)
fileObject.close()

#open('h3.bin', 'w+b').write(iso.getPartitionH3Table())
#open('h3.bin', 'w+b').close()
#isoTik = Ticket('tik.bin')
#print '%s' % isoTik
#open('main.dol', 'w+b').write(iso.getPartitionMainDol())
#open('main.dol', 'w+b').close()
#isoTmd = TMD(iso.getPartitionTmd())
#print isoTmd
