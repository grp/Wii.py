import os, struct, subprocess, fnmatch, shutil, urllib, array

import time
from title import *
from Struct import Struct

from common import *


class WOD: #WiiOpticalDisc
	class fsentry:
		name = ""
		type = 0
		parent = None
		offset = 0
		lenght = 0
		
		def __init__(self, name, type, parent, offset, len):
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
		def __str__(self):
			ret = ''
			ret += '%s [%s%s%s]\n' % (self.title, self.discId, self.gameCode, self.region)
			if self.region == 'P':
				ret += 'Region : PAL\n'
			elif self.region == 'E':
				ret += 'Region : NTSC\n'
			elif self.region == 'J':
				ret += 'Region : JPN\n'
			ret += 'Version 0x%x Maker %i%i Audio streaming %x\n' % (self.version, self.makerCode[0], self.makerCode[1], self.audioStreaming)
			ret += 'Hash verify flag 0x%x H3 verify flag : 0x%x\n' % (self.hashVerify, self.h3verify)
			
			return ret
				
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
			ret += 'Apploader built on %s\n' % self.buildDate
			ret += 'Entry point 0x%x\n' % self.entryPoint
			ret += 'Size %i (%i of them are trailing)\n' % (self.size, self.trailingSize)
			
			return ret
	
	def __str__(self):
		ret = ''
		ret += '%s\n' % self.discHdr
		ret += 'Found %i partitions (table at 0x%x)\n' % (self.partitionCount, self.partsTableOffset)
		ret += 'Found %i channels (table at 0x%x)\n' % (self.channelsCount, self.chansTableOffset)
		ret += '\n'
		ret += 'Partition %i opened (type 0x%x) at 0x%x\n' % (self.partitionOpen, self.partitionType, self.partitionOffset)
		ret += '%s' % self.partitionHdr
		ret += 'Partition key %s\n' % hexdump(self.partitionKey)
		ret += 'Tmd at 0x%x (%x)\n' % (self.tmdOffset, self.tmdSize)
		ret += 'main.dol at 0x%x (%x)\n' % (self.dolOffset, self.dolSize)
		ret += 'FST at 0x%x (%x)\n' % (self.fstSize, self.fstOffset)
		ret += '%s\n' % (self.appLdr)
		
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
		
		self.markedBlocks = []
		
		self.partitionOpen = -1
		self.partitionOffset = -1
		self.partitionType = -1
		
	def markContent(self, offset, size):
		blockStart = offset / 0x7C00
		blockLen = (align(size, 0x7C00)) / 0x7C00
		
		for x in range(blockStart, blockLen):
			try:
				self.markedBlocks.index(blockStart + x)
			except:
				self.markedBlocks.append(blockStart + x)
				
		#print '%s (%i blocks marked)' % (self.markedBlocks, len(self.markedBlocks))
	def decryptBlock(self, block):
		if len(block) != 0x8000:
			raise Exception('Block size too big/small')	
			
		blockIV = block[0x3d0:0x3e0]
		#print 'IV %s (len %i)\n' % (hexdump(blockIV), len(blockIV))
		blockData = block[0x0400:0x8000]
		
		return Crypto().decryptData(self.partitionKey, blockIV, blockData, True)
		
	def readPartition(self, offset, size):
		
		readStart = offset / 0x7C00
		readLen = (align(size, 0x7C00)) / 0x7C00
		blob = ''
		
		#print 'Read at 0x%x (Start on %i block, ends at %i block) for %i bytes' % (offset, readStart, readStart + readLen, size)
		
		self.fp.seek(self.partitionOffset + 0x20000 + (0x8000 * readStart))

		for x in range(readLen + 1):
			blob += self.decryptBlock(self.fp.read(0x8000))
		
		self.markContent(offset, size)
		
		#print 'Read from 0x%x to 0x%x' % (offset, offset + size)
		offset -= readStart * 0x7C00
		return blob[offset:offset + size]
		
	def readUnencrypted(self, offset, size):
		if offset > 0x20000:
			raise Exception('This read is on encrypted data')
			
		# FIXMII : Needs testing, extracting the tmd cause to have 10 null bytes in the end instead of 10 useful bytes at start :|
		self.fp.seek(self.partitionOffset + 0x2A4 + offset)
		return self.fp.read(size)
	class fstObject(object):
		#TODO: add ability to extract file by path
		def __init__(self, name, iso=None):
			''' do init stuff here '''
			self.parent = None
			self.type = 1 #directory: 1, file:0
			self.name = name
			self.nameOff = 0
			self.fileOffset = 0
			self.size = 0
			self.children = []
			self.iso = iso
		def addChild(self, child):
			if self.type == 0:
				raise Exception('I am not a directory.')
			child.parent = self
			self.children.append(child)
		def getISO(self):
			if(self.parent == None):
				return self.iso
			return self.parent.getISO()
		def getList(self, pad=0):
			if self.type == 0:
				return ("\t" * pad) + self.getPath() + "\n"
			str = "%s[%s]\n" % ("\t" * (pad), self.getPath())
			for child in self.children:
				str += child.getList(pad+1)
			return str
		def count(self):
			if self.type == 0:
				return 1
			i = 0
			for child in self.children:
				i += child.count()
			return i
		def getPath(self):
			if(self.parent == None):
				return "/"
			if(self.type == 1):
				return self.parent.getPath() + self.name + "/"
			return self.parent.getPath() + self.name
		def write(self, cwd):
			if(self.type==0):
				print cwd + self.getPath()
				#print self.nameOff
				open(cwd + self.getPath(), 'w+b').write(self.getISO().readPartition(self.fileOffset, self.size))
			if(self.type==1):
				if(self.parent != None):
					try:
						os.makedirs(cwd + self.getPath())
					except:
						j = None	
				for child in self.children:
					child.write(cwd)
	def parseFst(self, fst, names, i, fstDir):	
		size = struct.unpack(">I", fst[(12*i + 8):(12*i + 8) + 4])[0]
		nameOff = struct.unpack(">I", fst[(12*i):(12*i) + 4])[0] & 0x00ffffff
		fileName = names[nameOff:]
		fileName = fileName[:fileName.find('\0')]
			
		if i == 0:
			j = 1
			while(j<size):
				j = self.parseFst(fst, names, j, fstDir)
			return size
		if fst[12 * i] == '\x01':
			newDir = self.fstObject(fileName)
			j = i+1
			while(j<size):
				j = self.parseFst(fst, names, j, newDir)
			fstDir.addChild(newDir)
			return size
		else:
			fileOffset = 4 * struct.unpack(">I", fst[(12*i + 4):(12*i + 4) + 4])[0]
			newFile = self.fstObject(fileName)
			newFile.type = 0
			newFile.fileOffset = fileOffset
			newFile.size = size
			newFile.nameOff = nameOff
			fstDir.addChild(newFile)
			#self.markContent(fileOffset, size)
			return i+1

	def openPartition(self, index):
		if index+1 > self.partitionCount:
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
		
		self.fstOffset = 4 * struct.unpack(">I", self.readPartition (0x424, 4))[0]
		self.fstSize = 4 * struct.unpack(">I", self.readPartition (0x428, 4))[0]
		
		self.dolOffset = 4 * struct.unpack(">I", self.readPartition (0x420, 4))[0]
		self.dolSize = self.fstOffset - self.dolOffset
	
		self.appLdr = self.Apploader().unpack(self.readPartition (0x2440, 32))
		self.partitionHdr = self.discHeader().unpack(self.readPartition (0x0, 0x400))

	def getFst(self):
		fstBuf = self.readPartition(self.fstOffset, self.fstSize)
		return fstBuf
		
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
		return self.readUnencrypted(self.certsOffset, self.certsSize)
		
	def getPartitionH3Table(self):
		return self.readUnencrypted(self.H3TableOffset, 0x18000)
		
	def getPartitionTmd(self):
		return self.readUnencrypted(self.tmdOffset, self.tmdSize)
		
	def getPartitionTik(self):
		self.fp.seek(self.partitionOffset)
		return self.fp.read(0x2A4)
		
	def getPartitionApploader(self):
		return self.readPartition (0x2440, self.appLdr.size + self.appLdr.trailingSize + 32)
		
	def getPartitionMainDol(self):
		return self.readPartition (self.dolOffset, self.dolSize)

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
		
		
