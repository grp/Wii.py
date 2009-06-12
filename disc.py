import os, hashlib, struct, subprocess, fnmatch, shutil, urllib, array
import wx
import png

from Crypto.Cipher import AES
from Struct import Struct

from common import *


class WOD: #WiiOpticalDisc
	def __init__(self, f):
		self.f = f
		
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
		
		
	def extractPartition(self, index, fn = ""):
		self.fp = open(self.f, "rb")
		
		if(fn == ""):
			fn = os.path.dirname(self.f) + "/" + os.path.basename(self.f).replace(".", "_") + "_out"
		try:
			origdir = os.getcwd()
			os.mkdir(fn)
		except:
			pass
		os.chdir(fn)
		
		self.titleid = self.fp.read(4)
		self.publisher = self.fp.read(2)
		
		self.fp.seek(0x18)
		if(struct.unpack(">I", self.fp.read(4))[0] != 0x5D1C9EA3):
			self.fp.seek(-4, 1)
			raise ValueError("Not a valid Wii Disc (GC not supported)! Magic: %08x" % struct.unpack(">I", self.fp.read(4))[0])
			
		self.fp.seek(0x40000)
		partitions = struct.unpack(">I", self.fp.read(4))[0]
		parttableoffs = struct.unpack(">I", self.fp.read(4))[0] << 2
		
		channels = struct.unpack(">I", self.fp.read(4))[0]
		chantableoffs = struct.unpack(">I", self.fp.read(4))[0] << 2
		
		self.fp.seek(parttableoffs + (8 * index))
		partitionoffs = struct.unpack(">I", self.fp.read(4))[0] << 2
		partitiontype = struct.unpack(">I", self.fp.read(4))[0] #0 is data, 1 is update, 2 is installer
		
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
		
		
