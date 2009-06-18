import os, hashlib, struct, subprocess, fnmatch, shutil, urllib, array
import wx
import png

from title import *
from Crypto.Cipher import AES
from Struct import Struct

from common import *


class WOD: #WiiOpticalDisc
	class fsentry:
		name = ""
		parent = None
		
		def __init__(self, name, parent):
			self.name = ""
			if(parent != None):
				self.parent = parent
		def path(self):
			return parent.path() + "/" + name
			
	class fsdir(fsentry):
		def __init__(self, name, parent):
			fsentry.__init__(self, name, parent)
			
	class fsfile(fsentry):
		size = 0
		offset = 0
		
	class discHeader(Struct):
		__endian__ = Struct.BE
		def __format__(self):
			self.discId = Struct.string(1)
			self.gameCode = Struct.string(2)
			self.region = Struct.string(1)
			self.makerCode = Struct.uint8[2]
			self.h = Struct.uint8
			self.version = Struct.uint8
			self.audioStreaming = Struct.uint8
			self.streamingBufSize = Struct.uint8
			self.unused = Struct.uint8[14]
			self.magic = Struct.uint32
			self.title = Struct.string(64)
			self.hashVerify = Struct.uint8
			self.h3verify = Struct.uint8
			
	# Many many thanks to Wiipower
	class Apploader(Struct):
		__endian__ = Struct.BE
		def __format__(self):
			self.buildDate = Struct.string(16)
			self.entryPoint = Struct.uint32
			self.size = Struct.uint32
			self.trailingSize = Struct.uint32
			self.padding = Struct.uint8[4]
	
	def __str__(self):
		ret = ''
		ret += '%s [%s%s%s]\n' % (self.discHdr.title, self.discHdr.discId, self.discHdr.gameCode, self.discHdr.region)
		if self.discHdr.region == 'P':
			ret += 'Region : PAL\n'
		elif self.discHdr.region == 'E':
			ret += 'Region : NTSC\n'
		elif self.discHdr.region == 'J':
			ret += 'Region : JPN\n'
		ret += 'Version 0x%x Maker %i%i Audio streaming %x\n' % (self.discHdr.version, self.discHdr.makerCode[0], self.discHdr.makerCode[1], self.discHdr.audioStreaming)
		ret += 'Hash verify flag 0x%x H3 verify flag : 0x%x\n' % (self.discHdr.hashVerify, self.discHdr.h3verify)
		ret += 'Found %i partitions (table at 0x%x)\n' % (self.partitionCount, self.partsTableOffset)
		ret += 'Found %i channels (table at 0x%x)\n' % (self.channelsCount, self.chansTableOffset)
		ret += 'Partition %i opened (type 0x%x) at 0x%x)\n' % (self.partitionOpen, self.partitionType, self.partitionOffset)
		ret += 'Partition title : %s\n' % self.partitionHdr.title
		ret += 'Partition key %s\n' % hexdump(self.partitionKey)
		ret += 'Tmd at 0x%x\n' % self.tmdOffset
		ret += 'main.dol at 0x%x fst at 0x%x (%xb)\n' % (self.dolOffset, self.fstSize, self.fstOffset)
		ret += 'Apploader built on %s (%x bytes)\n' % (self.appLdr.buildDate, self.appLdr.size + self.appLdr.trailingSize)
		
		return ret
				
	def __init__(self, f):
		self.f = f
		self.fp = open(f, 'rb')
		
		self.discHdr = self.discHeader().unpack(self.fp.read(0x400))
		if self.discHdr.magic != 0x5D1C9EA3:
			raise Exception('Wrong disc magic')
					
		self.fp.seek(0x40000)
			
		self.partitionCount = 1 + struct.unpack(">I", self.fp.read(4))[0]
		self.partsTableOffset = struct.unpack(">I", self.fp.read(4))[0] << 2
		
		self.channelsCount = struct.unpack(">I", self.fp.read(4))[0]
		self.chansTableOffset = struct.unpack(">I", self.fp.read(4))[0] << 2
		
		self.partitionOpen = -1
		self.partitionOffset = -1
		self.partitionType = -1
		
	def decryptBlock(self, block):
		if len(block) != 0x8000:
			raise Exception('Block size too big/small')	
			
		blockIV = block[0x3d0:0x3dF + 1]
		print 'IV %s (len %i)\n' % (hexdump(blockIV), len(blockIV))
		blockData = block[0x0400:0x7FFF]
		
		return Crypto().DecryptData(self.partitionKey, blockIV, blockData, True)
		
		
	def openPartition(self, index):
		if index > self.partitionCount:
			raise ValueError('Partition index too big')
			
		self.partitionOpen = index
		
		self.partitionOffset = self.partsTableOffset + (8 * self.partitionOpen)
		
		self.fp.seek(self.partsTableOffset + (8 * self.partitionOpen))
		
		self.partitionOffset = struct.unpack(">I", self.fp.read(4))[0] << 2
		self.partitionType = struct.unpack(">I", self.fp.read(4))[0]
		
		self.fp.seek(self.partitionOffset)
		
		self.tikData = self.fp.read(0x2A4)
		self.partitionKey = Ticket(self.tikData).getTitleKey()
		
		self.tmdSize = struct.unpack(">I", self.fp.read(4))[0]
		self.tmdOffset = struct.unpack(">I", self.fp.read(4))[0] >> 2
		
		self.certsSize = struct.unpack(">I", self.fp.read(4))[0]
		self.certsOffset = struct.unpack(">I", self.fp.read(4))[0] >> 2
		
		self.H3TableOffset = struct.unpack(">I", self.fp.read(4))[0] >> 2
		
		self.dataOffset = struct.unpack(">I", self.fp.read(4))[0] >> 2
		self.dataSize = struct.unpack(">I", self.fp.read(4))[0] >> 2
		
		self.dolOffset = 4 * struct.unpack(">I", self.readPartition (0x420, 4))[0]
		
		self.fstOffset = 4 * struct.unpack(">I", self.readPartition (0x424, 4))[0]
		self.fstSize = 4 * struct.unpack(">I", self.readPartition (0x428, 4))[0]
		
		self.appLdr = self.Apploader().unpack(self.readPartition (0x2440, 32))
		self.partitionHdr = self.discHeader().unpack(self.readPartition (0x0, 0x400))

	def readPartition(self, offset, size):
		if size > 0x8000:
			pass#raise Exception('To be implemented')
		
		readBlocks = size / 0x8000
		blockToRead = offset / 0x8000
		blob = ''
			
		print 'Read at 0x%x for %i bytes' % (offset, size)
		print 'Going to read %i blocks' % readBlocks
		
		self.fp.seek(self.partitionOffset + 0x20000 + (0x8000 * blockToRead))
		if readBlocks == 0:
			blob += self.decryptBlock(self.fp.read(0x8000))
		else:
			for x in range(readBlocks):
				blob += self.decryptBlock(self.fp.read(0x8000))
		
		print 'Read from 0x%x to 0x%x' % (offset, offset + size) 	
		return blob[offset:offset + size]
		
	def getIsoBootmode(self):
		if self.discHdr.discId == 'R' or self.discHdr.discId == '_':
			return 2
		elif self.discHdr.discId == '0':
			return 1
		
	def getOpenedPartition(self):
		return self.partitionOpen
		
	def getOpenedPartitionOffset(self):
		return self.partitionOffset
		
	def getOpenedPartitionType(self):
		return self.partitionType
		
	def getPartitionsCount(self):
		return self.partitionCount
		
	def getChannelsCount(self):
		return self.channelsCount
		
	def getPartitionCerts(self):
		self.fp.seek(self.partitionOffset + self.certsOffset)
		return self.fp.read(self.certsSize)
		
	def getPartitionH3Table(self):
		self.fp.seek(self.partitionOffset + self.H3TableOffset)
		return self.fp.read(0x18000)
		
	def getPartitionTmd(self):
		self.fp.seek(self.partitionOffset + self.tmdOffset)
		return self.fp.read(self.tmdSize)
		
	def getPartitionTik(self):
		self.fp.seek(self.partitionOffset)
		return self.fp.read(0x2A4)
		
	def getPartitionApploader(self):
		return self.readPartition (0x2460, self.appLdr.size + self.appLdr.trailingSize)

	def extractPartition(self, index, fn = ""):

		if(fn == ""):
			fn = os.path.dirname(self.f) + "/" + os.path.basename(self.f).replace(".", "_") + "_out"
		try:
			origdir = os.getcwd()
			os.mkdir(fn)
		except:
			pass
		os.chdir(fn)
		
		self.fp.seek(0x18)
		if(struct.unpack(">I", self.fp.read(4))[0] != 0x5D1C9EA3):
			self.fp.seek(-4, 1)
			raise ValueError("Not a valid Wii Disc (GC not supported)! Magic: %08x" % struct.unpack(">I", self.fp.read(4))[0])

		self.fp.seek(partitionoffs)
		
		tikdata = self.fp.read(0x2A3)
		open("tik").write(tikdata)
		self.tik = Ticket("tik")
		self.titlekey = self.tik.getTitleKey()
		
		tmdsz = struct.unpack(">I", self.fp.read(4))[0]
		tmdoffs = struct.unpack(">I", self.fp.read(4))[0]
		
		certsz = struct.unpack(">I", self.fp.read(4))[0]
		certoffs = struct.unpack(">I", self.fp.read(4))[0]
		
		h3offs = struct.unpack(">I", self.fp.read(4))[0] << 2
		h3sz = 0x18000
		
		dataoffs = struct.unpack(">I", self.fp.read(4))[0] << 2
		datasz = struct.unpack(">I", self.fp.read(4))[0] << 2
		if(tmdoffs != self.fp.tell()):
			raise ValueError("TMD is in wrong place, something is fucked...wtf?")
		
		tmddata = self.fp.read(tmdsz)
		open("tmd").write(tmddata)
		
		self.tmd = TMD("tmd")
		
		
		print tmd.getIOSVersion()
		
		
		fst.seek(dataoffs)
		
		
		
		os.chdir("..")
	def _recurse(self, parent, names, recursion):		
		if(recursion == 0):
			pass	
		
		
