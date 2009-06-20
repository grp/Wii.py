import os, hashlib, struct, subprocess, fnmatch, shutil, urllib, array
import wx
import png
from binascii import *

from Crypto.Cipher import AES
from Struct import Struct
from struct import *

from common import *
from title import *

class CONF:
	""" This class deal with setting.txt wich hold some wii info like game area and wii serial number """
	
	def __init__(self, f):
		self.conf = ''
		self.keys = {}
		self.keyNames = []
		self.lastKeyOffset = 0
		self.totalKeys = 0
		
		try:
			self.fp = open(f, 'r+b')
		except:
			self.fp = open(f, 'w+b')
			return
			
		self.conf = self.fp.read(0x100)
		self.conf = self.xorConf(self.conf)
		self.fp.seek(0)
	
		keys = self.conf.split('\r\n')
		
		self.lastKeyOffset = self.conf.rfind('\r\n') + 2
		self.totalKeys = len(keys) - 1
	
		for x in range(self.totalKeys):
			keyName = keys[x].split('=')[0]
			keyVal = keys[x].split('=')[1]
			
			self.keyNames.append(keyName)
			self.keys[keyName] = keyVal

	def getKeysCount(self):
		return self.totalKeys		
			
	def getKeysName(self):
		return self.keyNames

	def getKeyValue(self, key):
		try:
			return self.keys[key.upper()]
		except KeyError:
			return 'Key not found'
			
	def setKeyValue(self, key, value):
		if self.getKeyValue(key.upper()) != 'Key not found':
			self.keys[key.upper()] = value.upper()
			
		self.conf = ''
			
		for key in self.keys:
			self.conf += key
			self.conf += '='
			self.conf += self.keys[key]
			self.conf += '\r\n'
			
		self.fp.seek(0)
		self.fp.write(self.xorConf(self.conf))
		self.fp.write('\x00' * (0x100 - len(self.conf)))
			
		self.lastKeyOffset = self.conf.rfind('\r\n') + 2
	
	def keyExist(self, key):
		if self.getKeyValue(key.upper()) != 'Key not found':
			return 0
		else:
			return 1
				
	def addKey(self, key, value):
		if self.lastKeyOffset + len(key) + 1 + len(value) + 2 > 0x100:
			return -1
		if not self.keyExist(key):
			return -2
			
		self.keys[key.upper()] = value.upper()
		self.keyNames.append(key.upper())
		self.totalKeys +=1
			
		self.conf = self.conf[:self.lastKeyOffset] + key.upper() + '=' + value.upper() + '\r\n'
		
		self.lastKeyOffset += len(key) + 1 + len(value) + 2

		self.fp.seek(0)
		self.fp.write(self.xorConf(self.conf))	

	def xorConf(self, conf):
		xorKey = 0x73B5DBFA
		out = ''
		for x in range(len(conf)):
			out += chr(ord(conf[x]) ^ xorKey & 0xFF)
			xorKey = (xorKey << 1) | (xorKey >> 31)
			
		return out
	
class iplsave:
	"""This class performs all iplsave.bin related things. It includes functions to add a title to the list, remove a title based upon position or title,  and move a title from one position to another."""
	class IPLSAVE_Entry(Struct):
		__endian__ = Struct.BE
		def __format__(self):
			self.type1 = Struct.uint8
			self.type2 = Struct.uint8
			self.unk = Struct.uint32
			self.flags = Struct.uint16
			self.titleid = Struct.uint64

	class IPLSAVE_Header(Struct):
		__endian__ = Struct.BE
		def __format__(self):
			self.magic = Struct.string(4)
			self.filesize = Struct.uint32
			self.unk = Struct.uint64
			# 0x30 Entries go here.
			self.unk2 = Struct.string(0x20)
			self.md5 = Struct.string(0x10)

	def __init__(self, f):
		self.f = f
		if(not os.path.isfile(f)):
			baseipl_h = self.IPLSAVE_Header
			baseipl_ent = self.IPLSAVE_Entry
			baseipl_ent.type1 = 0
			baseipl_ent.type2 = 0
			baseipl_ent.unk = 0
			baseipl_ent.flags = 0
			baseipl_ent.titleid = 0
			baseipl_h.magic = "RIPL"
			baseipl_h.filesize = 0x340
			baseipl_h.unk = 0x0000000200000000
			baseipl_h.unk2 = "\0" * 0x20
			fp = open(f, "wb")
			fp.write(baseipl_h.magic)
			fp.write(a2b_hex("%08X" % baseipl_h.filesize))
			fp.write(a2b_hex("%016X" % baseipl_h.unk))
			i = 0
			for i in range(0x30):
				fp.write(a2b_hex("%02X" % baseipl_ent.type1))
				fp.write(a2b_hex("%02X" % baseipl_ent.type2))
				fp.write(a2b_hex("%08X" % baseipl_ent.unk))
				fp.write(a2b_hex("%04X" % baseipl_ent.flags))
				fp.write(a2b_hex("%016X" % baseipl_ent.titleid))
			fp.write(baseipl_h.unk2)
			fp.close()
			self.UpdateMD5()

	def UpdateMD5(self):
		fp = open(self.f, "rb")
		data = fp.read()
		fp.close()
		md5 = Crypto().CreateMD5Hash(data)
		fp = open(self.f, "wb")
		fp.write(data)
		fp.write(md5)
		fp.close()

	def AddTitleBase(self, x, y, page, tid, movable, type, overwrite, clear, isdisc):
		if((x + (y * 4) + (page * 12)) >= 0x30):
			print "Too far!"
			return None
		fp = open(self.f, "rb")
		data = fp.read()
		fp.seek(16 + ((x + (y * 4) + (page * 12))) * 16)
		baseipl_ent = self.IPLSAVE_Entry
		baseipl_ent.type1 = fp.read(1)
		fp.close()
		if((baseipl_ent.type1 != "\0") and (not overwrite)):
			return self.AddTitle(x + 1, y, page, tid, movable, type)
		fp = open(self.f, "wb")
		fp.write(data)
		fp.seek(16 + ((x + (y * 4) + (page * 12))) * 16)
		if((not clear) and (not isdisc)):
			baseipl_ent.type1 = 3
			baseipl_ent.type2 = type
			baseipl_ent.unk = 0
			baseipl_ent.flags = (movable ^ 1) + 0x0E
			baseipl_ent.titleid = tid
		if((clear) and (not isdisc)):
			baseipl_ent.type1 = 0
			baseipl_ent.type2 = 0
			baseipl_ent.unk = 0
			baseipl_ent.flags = 0
			baseipl_ent.titleid = 0
		if(isdisc):
			baseipl_ent.type1 = 1
			baseipl_ent.type2 = 1
			baseipl_ent.unk = 0
			baseipl_ent.flags = (movable ^ 1) + 0x0E
			baseipl_ent.titleid = 0
		fp.write(a2b_hex("%02X" % baseipl_ent.type1))
		fp.write(a2b_hex("%02X" % baseipl_ent.type2))
		fp.write(a2b_hex("%08X" % baseipl_ent.unk))
		fp.write(a2b_hex("%04X" % baseipl_ent.flags))
		fp.write(a2b_hex("%016X" % baseipl_ent.titleid))
		fp.close()
		self.UpdateMD5()
		return (x + (y * 4) + (page * 12))

	def AddTitle(self, x, y, page, tid, movable, type):
		return self.AddTitleBase(x, y, page, tid, movable, type, 0, 0, 0)

	def AddDisc(self, x, y, page, movable):
		return self.AddTitleBase(x, y, page, 0, movable, 0, 0, 0, 1)

	def DeletePosition(self, x, y, page):
		return self.AddTitleBase(x, y, page, 0, 0, 0, 1, 1, 0)

	def DeleteTitle(self, tid):
		fp = open(self.f, "rb")
		baseipl_ent = self.IPLSAVE_Entry
		for i in range(0x30):
			fp.seek(16 + (i * 16))
			baseipl_ent.type1 = fp.read(1)
			baseipl_ent.type2 = fp.read(1)
			baseipl_ent.unk = fp.read(4)
			baseipl_ent.flags = fp.read(2)
			baseipl_ent.titleid = fp.read(8)
			if(baseipl_ent.titleid == a2b_hex("%016X" % tid)):
				self.DeletePosition(i, 0, 0)
		fp.close()

	def MoveTitle(self, x1, y1, page1, x2, y2, page2):
		fp = open(self.f, "rb")
		baseipl_ent = self.IPLSAVE_Entry
		fp.seek(16 + ((x1 + (y1 * 4) + (page1 * 12)) * 16))
		baseipl_ent.type1 = fp.read(1)
		baseipl_ent.type2 = fp.read(1)
		baseipl_ent.unk = fp.read(4)
		baseipl_ent.flags = fp.read(2)
		baseipl_ent.titleid = fp.read(8)
		fp.close()
		self.DeletePosition(x1, y1, page1)
		return self.AddTitle(x2, y2, page2, baseipl_ent.titleid, (baseipl_ent.flags - 0xE) ^ 1, baseipl_ent.type2)
