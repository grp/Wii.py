import os, hashlib, struct, subprocess, fnmatch, shutil, urllib, array
from binascii import *

from Crypto.Cipher import AES
from Struct import Struct
from struct import *

from common import *
from title import *

class CONF:
	"""This class deals with setting.txt which holds some important information like region and serial number """
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
		self.conf = self.XORConf(self.conf)
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
		"""Gets how many keys exist."""
		return self.totalKeys		
			
	def getKeysName(self):
		"""Returns the list of key names."""
		return self.keyNames

	def getKeyValue(self, key):
		"""Returns the value of the key ``key''."""
		try:
			return self.keys[key.upper()]
		except KeyError:
			return 'Key not found'
			
	def setKeyValue(self, key, value):
		"""Sets the value of key ``key'' to ``value''."""
		if(self.keyExist(key)):
			self.keys[key.upper()] = value.upper()
			
		self.conf = ''
			
		for key in self.keys:
			self.conf += key
			self.conf += '='
			self.conf += self.keys[key]
			self.conf += '\r\n'
			
		self.fp.seek(0)
		self.fp.write(self.XORConf(self.conf))
		self.fp.write('\x00' * (0x100 - len(self.conf)))
			
		self.lastKeyOffset = self.conf.rfind('\r\n') + 2
	
	def keyExist(self, key):
		"""Returns 1 if key ``key'' exists, 0 otherwise."""
		if self.getKeyValue(key.upper()) != 'Key not found':
			return 0
		else:
			return 1
				
	def addKey(self, key, value):
		"""Adds key ``key'' with value ``value'' to the list."""
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
		self.fp.write(self.XORConf(self.conf))	

	def XORConf(self, conf):
		"""Encrypts/decrypts the setting.txt file."""
		XORKey = 0x73B5DBFA
		out = ''
		for x in range(len(conf)):
			out += chr(ord(conf[x]) ^ XORKey & 0xFF)
			XORKey = (XORKey << 1) | (XORKey >> 31)
			
		return out
	
	def DeleteKey(self, key):
		"""Deletes the key ``key''."""
		try:
			del self.keys[key.upper()]
			self.keyNames.remove(key.upper())
			self.totalKeys -=1
		    
			self.conf = ''
      
			for key in self.keys:
				self.conf += key
				self.conf += '='
				self.conf += self.keys[key]
				self.conf += '\r\n'
      
			self.fp.seek(0)
			self.fp.write(self.XORConf(self.conf))
			self.fp.write('\x00' * (0x100 - len(self.conf)))
      
			self.lastKeyOffset = self.conf.rfind('\r\n') + 2
		except KeyError:
			return 'Key not found'

# This function is fucking dangerous. It deletes all keys with that value. Really not a good idea.
	def deleteKeyByValue(self, value):
		"""Deletes all keys with value ``value''. WATCH OUT, YOU MIGHT ACCIDENTALLY DELETE WRONG KEYS."""
		try:
			for key in self.keys.keys():
				if self.keys.get(key) == value: 
					del self.keys[key]
					self.keyNames.remove(key)
					self.totalKeys -=1
			
		    
			self.conf = ''
      
			for key in self.keys:
				self.conf += key
				self.conf += '='
				self.conf += self.keys[key]
				self.conf += '\r\n'
     
			self.fp.seek(0)
			self.fp.write(self.XORConf(self.conf))
			self.fp.write('\x00' * (0x100 - len(self.conf)))
      
			self.lastKeyOffset = self.conf.rfind('\r\n') + 2
		except KeyError:
			return 'Key not found'

	def getRegion(self):
		"""gets the Region key. (Shortcut for getKeyValue("GAME"))"""
		return self.getKeyValue("GAME")

	def getArea(self):
		"""gets the Area key. (Shortcut for getKeyValue("AREA"))"""
		return self.getKeyValue("AREA")

	def getVideoMode(self):
		"""gets the Video Mode key. (Shortcut for getKeyValue("VIDEO"))"""
		return self.getKeyValue("VIDEO")

	def getSerialCode(self):
		"""gets the Serial Code key. (Shortcut for getKeyValue("CODE"))"""
		return self.getKeyValue("CODE")

	def getDVDModel(self): # Might not be model =/
		"""gets the DVD Model (?) key. (Shortcut for getKeyValue("DVD"))"""
		return self.getKeyValue("DVD")

	def getHardwareModel(self):
		"""gets the Hardware Model key. (Shortcut for getKeyValue("MODEL"))"""
		return self.getKeyValue("MODEL")

	def getSerialNumber(self):
		"""gets the Serial Number key. (Shortcut for getKeyValue("SERNO"))"""
		return self.getKeyValue("SERNO")


	def setRegion(self, value):
		"""sets the Region key. (Shortcut for setKeyValue("GAME", value))"""
		return self.setKeyValue("GAME", value)

	def setArea(self, value):
		"""sets the Area key. (Shortcut for setKeyValue("AREA", value))"""
		return self.setKeyValue("AREA", value)

	def setVideoMode(self, value):
		"""sets the Video Mode key. (Shortcut for setKeyValue("VIDEO", value))"""
		return self.setKeyValue("VIDEO", value)

	def setSerialCode(self, value):
		"""sets the Serial Code key. (Shortcut for setKeyValue("CODE", value))"""
		return self.setKeyValue("CODE", value)

	def setDVDModel(self, value): # Might not be model =/
		"""sets the DVD Model (?) key. (Shortcut for setKeyValue("DVD", value))"""
		return self.setKeyValue("DVD", value)

	def setHardwareModel(self, value):
		"""sets the Hardware Model key. (Shortcut for setKeyValue("MODEL", value))"""
		return self.setKeyValue("MODEL", value)

	def setSerialNumber(self, value):
		"""sets the Serial Number key. (Shortcut for setKeyValue("SERNO", value))"""
		return self.setKeyValue("SERNO", value)


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

	def updateMD5(self):
		"""Updates the MD5 hash in the iplsave.bin file. Used by other functions here."""
		fp = open(self.f, "rb")
		data = fp.read()
		fp.close()
		md5 = Crypto().createMD5Hash(data)
		fp = open(self.f, "wb")
		fp.write(data)
		fp.write(md5)
		fp.close()

	def addTitleBase(self, x, y, page, tid, movable, type, overwrite, clear, isdisc):
		"""A base AddTitle function that is used by others. Don't use this."""
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
			return self.addTitleBase(x + 1, y, page, tid, movable, type, overwrite, clear, isdisc)
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
		self.updateMD5()
		return (x + (y * 4) + (page * 12))

	def addTitle(self, x, y, page, tid, movable, type):
		"""Adds a title with title ID ``tid'' at location (x,y) on page ``page''. ``movable'' specifies whether the title is movable, and ``type'' specifies the type of title (00 for most titles.)"""
		return self.addTitleBase(x, y, page, tid, movable, type, 0, 0, 0)

	def addDisc(self, x, y, page, movable):
		"""Adds the Disc Channel at location (x,y) on page ``page''. ``movable'' specifies whether it can be moved."""
		return self.addTitleBase(x, y, page, 0, movable, 0, 0, 0, 1)

	def deletePosition(self, x, y, page):
		"""Deletes the title at (x,y) on page ``page''"""
		return self.addTitleBase(x, y, page, 0, 0, 0, 1, 1, 0)

	def deleteTitle(self, tid):
		"""Deletes the title with title ID ``tid''"""
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
				self.deletePosition(i, 0, 0)
		fp.close()

	def moveTitle(self, x1, y1, page1, x2, y2, page2):
		"""Moves a title from (x1,y1) on page ``page1'' to (x2,y2) on page ``page2''"""
		fp = open(self.f, "rb")
		baseipl_ent = self.IPLSAVE_Entry
		fp.seek(16 + ((x1 + (y1 * 4) + (page1 * 12)) * 16))
		baseipl_ent.type1 = fp.read(1)
		baseipl_ent.type2 = fp.read(1)
		baseipl_ent.unk = fp.read(4)
		baseipl_ent.flags = fp.read(2)
		baseipl_ent.titleid = fp.read(8)
		fp.close()
		self.deletePosition(x1, y1, page1)
		return self.addTitle(x2, y2, page2, baseipl_ent.titleid, (baseipl_ent.flags - 0xE) ^ 1, baseipl_ent.type2)
