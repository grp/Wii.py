from binascii import *
import struct

from common import *
from title import *

class locDat:
	class locHeader(Struct):
		def __format__(self):
			self.magic = Struct.string(4)
			self.md5 = Struct.string(16)

	def __init__(self, f):
		self.sdKey = '\xab\x01\xb9\xd8\xe1\x62\x2b\x08\xaf\xba\xd8\x4d\xbf\xc2\xa5\x5d'
		self.sdIv = '\x21\x67\x12\xe6\xaa\x1f\x68\x9f\x95\xc5\xa2\x23\x24\xdc\x6a\x98'
		
		self.titles = []
		self.usedBlocks = 0
		self.freeBlocks = 0
		
		try:
			self.fp = open(f, 'r+')
		except:
			raise Exception('File not found')
			
		plainBuffer = Crypto().decryptData(self.sdKey, self.sdIv, self.fp.read(), False)	
			
		self.hdr = self.locHeader().unpack(plainBuffer[:0x14])
		
		for x in range(240):
			self.titles.append(plainBuffer[0x14 + x * 4:0x14 + (x + 1) * 4])
			if self.titles[x] == '\x00\x00\x00\x00':
				self.freeBlocks += 1
				
		self.usedBlocks = 240 - self.freeBlocks 
		
	def __str__(self):
		out = ''
		out += 'Used %i blocks out of 240\n\n' % self.usedBlocks
		for x in range(240):
			if self.titles[x] == '\x00\x00\x00\x00':
				out += 'Block %i on page %i is empty\n' % (x, x / 12)
			else:
				out += 'Block %i on page %i hold title %s\n' % (x, x / 12, self.titles[x])
				
		return out
				
	def getFreeBlocks(self):
		return self.freeBlocks 
		
	def getUsedBlocks(self):
		return self.usedBlocks
		
	def isBlockFree(self, x, y, page):
		if self.titles[((x + (y * 4) + (page * 12)))] == '\x00\x00\x00\x00':
			return 1
			
		return 0
			
	def isTitleInList(self, title):
		try:
			return self.titles.index(title.upper())
		except:
			return -1
			
	def getPageTitles(self, page):
		if page > 19:
			raise Exception('Out of bounds')
			
		return self.titles[12 * page:12 * (page + 1)]
			
	def getTitle(self, x, y, page):
		if x > 3 or y > 2 or page > 19:
			raise Exception('Out of bounds')
			
		return self.titles[((x + (y * 4) + (page * 12)))]
		
	def setTitle(self, x, y, page, element):
		if x > 3 or y > 2 or page > 19 or len(element) > 4:
			raise Exception('Out of bounds')
			
		self.titles[((x + (y * 4) + (page * 12)))] = element.upper()
		
		titles = ''
		
		titles += self.hdr.magic
		titles += self.hdr.md5
		
		for x in range(240):
			titles += self.titles[x]
			
		titles += '\x00' * 12
		
		titles = titles[:0x4] + Crypto().createMD5Hash(titles) + titles[0x14:]

		self.fp.seek(0)
		self.fp.write(Crypto().encryptData(self.sdKey, self.sdIv, titles))
			
	def delTitle(self, x, y, page):
		self.setTitle(x, y, page, '\x00\x00\x00\x00')

class CONF:
	"""This class deals with setting.txt which holds some important information like region and serial number """
	def __init__(self, f):
		self.conf = ''
		self.keys = {}
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
			
			self.keys[keyName] = keyVal

	def getKeysCount(self):
		"""Gets how many keys exist."""
		return self.totalKeys		
			
	def getKeysName(self):
		"""Returns the list of key names."""
		return self.keys.keys()

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
		return self.keys.has_key(key.upper())
				
	def addKey(self, key, value):
		"""Adds key ``key'' with value ``value'' to the list."""
		if self.lastKeyOffset + len(key) + 1 + len(value) + 2 > 0x100:
			return -1
		if not self.keyExist(key):
			return -2
			
		self.keys[key.upper()] = value.upper()
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
	
	def deleteKey(self, key):
		"""Deletes the key ``key''."""
		try:
			del self.keys[key.upper()]
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

class netConfig:
	"""This class performs network configuration. The file is located on the NAND at /shared2/sys/net/02/config.dat."""
	class configEntry(Struct):
		__endian__ = Struct.BE
		def __format__(self):
			self.selected = Struct.uint8
			self.padding_1 = Struct.string(1987)
			self.ssid = Struct.string(32)
			self.padding_2 = Struct.uint8
			self.ssid_len = Struct.uint8
			self.padding_3 = Struct.string(2)
			self.padding_4 = Struct.uint8
			self.encryption = Struct.uint8	# OPEN: 0x00, WEP: 0x01, WPA-PSK (TKIP): 0x04, WPA2-PSK (AES): 0x05, WPA-PSK (AES): 0x06
			self.padding_5 = Struct.string(2)
			self.padding_6 = Struct.uint8
			self.key_len = Struct.uint8
			self.padding_7 = Struct.string(2)
			self.key = Struct.string(64)
			self.padding_3 = Struct.string(236)

	def __init__(self, conf):
		self.f = conf
		if(not os.path.isfile(self.f)):
			fp = open(self.f, "wb")
			fp.write("\x00\x00\x00\x00\x01\x07\x00\x00")
			fp.write("\x00" * 0x91C * 3)
			fp.close()
		fp = open(self.f, "rb")
		head = fp.read(8)
		if(head != "\x00\x00\x00\x00\x01\x07\x00\x00"):
			print("Config file is invalid!\n")

	def getNotBlank(self, config):
		fp = open(self.f, "rb")
		fp.seek(8 + (0x91C * config))
		sel = struct.unpack(">B", fp.read(1))[0]
		fp.close()
		if(sel & 0x20):
			return 1
		return 0


	def getIPType(self, config):
		if(not self.getNotBlank(config)):
			return None
		fp = open(self.f, "rb")
		fp.seek(8 + (0x91C * config))
		sel = struct.unpack(">B", fp.read(1))[0]
		if(sel & 0x04):
			return 0
		else:
			return 1
		fp.close()
		return sel

	def getWireType(self, config):
		if(not self.getNotBlank(config)):
			return None
		fp = open(self.f, "rb")
		fp.seek(8 + (0x91C * config))
		sel = struct.unpack(">B", fp.read(1))[0]
		if(sel & 0x02):
			return 0
		else:
			return 1
		fp.close()

	def getSSID(self, config):
		if(not self.getNotBlank(config)):
			return None
		fp = open(self.f, "rb")
		fp.seek(8 + (0x91C * config) + 2021)
		len = struct.unpack(">B", fp.read(1))[0]
		fp.seek(8 + (0x91C * config) + 1988)
		ssid = fp.read(len)
		fp.close()
		return ssid

	def getEncryptionType(self, config):
		if(not self.getNotBlank(config)):
			return None
		fp = open(self.f, "rb")
		fp.seek(8 + (0x91C * config) + 2025)
		crypt = struct.unpack(">B", fp.read(1))[0]
		type = ""
		if(crypt == 0):
			type = "OPEN"
		elif(crypt == 1):
			type = "WEP"
		elif(crypt == 4):
			type = "WPA (TKIP)"
		elif(crypt == 5):
			type = "WPA2"
		elif(crypt == 6):
			type = "WPA (AES)"
		else:
			print("Invalid crypto type %02X. Valid types are: ``OPEN'', ``WEP'', ``WPA (TKIP)'', ``WPA2'', or ``WPA (AES)''\n" % crypt)
			fp.close()
			return None
		fp.close()
		return type

	def getEncryptionKey(self, config):
		if(not self.getNotBlank(config)):
			return None
		fp = open(self.f, "rb")
		fp.seek(8 + (0x91C * config) + 2025)
		crypt = struct.unpack(">B", fp.read(1))[0]
		type = ""
		if(crypt == 0):
			type = "OPEN"
		elif(crypt == 1):
			type = "WEP"
		elif(crypt == 4):
			type = "WPA (TKIP)"
		elif(crypt == 5):
			type = "WPA2"
		elif(crypt == 6):
			type = "WPA (AES)"
		else:
			print("Invalid crypto type %02X. Valid types are: ``OPEN'', ``WEP'', ``WPA (TKIP)'', ``WPA2'', or ``WPA (AES)''\n" % crypt)
			fp.close()
			return None
		if(crypt != "\x00"):
			fp.seek(8 + (0x91C * config) + 2029)
			keylen = struct.unpack(">B", fp.read(1))[0]
			fp.seek(8 + (0x91C * config) + 2032)
			key = fp.read(keylen)
			fp.close()
			return key
		fp.close()
		return None

	def clearConfig(self, config):
		fp = open(self.f, "rb+")
		fp.seek(8 + (0x91C * config))
		sel = struct.unpack(">B", fp.read(1))[0]
		sel &= 0xDF
		fp.seek(8 + (0x91C * config))
		fp.write(struct.pack(">B", sel))
		fp.close()

	def setNotBlank(self, config):
		fp = open(self.f, "rb+")
		fp.seek(8 + (0x91C * config))
		sel = struct.unpack(">B", fp.read(1))[0]
		sel |= 0x20
		fp.seek(8 + (0x91C * config))
		fp.write(struct.pack(">B", sel))
		fp.close()

	def setIPType(self, config, static):
		fp = open(self.f, "rb+")
		fp.seek(8 + (0x91C * config))
		sel = struct.unpack(">B", fp.read(1))[0]
		if(not static):
			sel |= 0x04
		else:
			sel &= 0xFB
		fp.seek(8 + (0x91C * config))
		fp.write(struct.pack(">B", sel))
		fp.close()
		self.setNotBlank(config)

	def setWireType(self, config, wired):
		fp = open(self.f, "rb+")
		fp.seek(8 + (0x91C * config))
		sel = struct.unpack(">B", fp.read(1))[0]
		if(not wired):
			sel |= 0x02
		else:
			sel &= 0xFD
		fp.seek(8 + (0x91C * config))
		fp.write(struct.pack(">B", sel))
		fp.close()
		self.setNotBlank(config)

	def setSSID(self, config, ssid):
		fp = open(self.f, "rb+")
		fp.seek(8 + (0x91C * config) + 1988)
		fp.write(ssid)
		fp.seek(8 + (0x91C * config) + 2021)
		fp.write(a2b_hex("%02X" % len(ssid)))
		fp.close()
		self.setNotBlank(config)

	def setEncryption(self, config, crypt, key):
		fp = open(self.f, "rb+")
		fp.seek(8 + (0x91C * config) + 2025)
		if(crypt == "OPEN"):
			fp.write("\x00")
		elif(crypt == "WEP"):
			fp.write("\x01")
		elif(crypt == "WPA (TKIP)"):
			fp.write("\x04")
		elif(crypt == "WPA2"):
			fp.write("\x05")
		elif(crypt == "WPA (AES)"):
			fp.write("\x06")
		else:
			print("Invalid crypto type. Valid types are: ``OPEN'', ``WEP'', ``WPA (TKIP)'', ``WPA2'', or ``WPA (AES)''\n")
			fp.close()
			return
		if(crypt != "OPEN"):
			fp.seek(8 + (0x91C * config) + 2029)
			fp.write(a2b_hex("%02X" % len(key)))
			fp.seek(8 + (0x91C * config) + 2032)
			fp.write(key)
		fp.close()
		self.setNotBlank(config)
	
	def selectConfig(self, config):
		fp = open(self.f, "rb+")
		fp.seek(8 + (0x91C * 0))
		sel = struct.unpack(">B", fp.read(1))[0]
		if(config == 0):
			sel |= 0x80
		else:
			sel &= 0x7F
		fp.seek(8 + (0x91C * 0))
		fp.write(struct.pack(">B", sel))
		fp.seek(8 + (0x91C * 1))
		sel = struct.unpack(">B", fp.read(1))[0]
		if(config == 1):
			sel |= 0x80
		else:
			sel &= 0x7F
		fp.seek(8 + (0x91C * 1))
		fp.write(struct.pack(">B", sel))
		fp.seek(8 + (0x91C * 2))
		sel = struct.unpack(">B", fp.read(1))[0]
		if(config == 2):
			sel |= 0x80
		else:
			sel &= 0x7F
		fp.seek(8 + (0x91C * 2))
		fp.write(struct.pack(">B", sel))
		self.setNotBlank(config)
		fp.close()


class ContentMap:
	"""This class performs all content.map related actions. Has functions to add contents, and find contents by hash.
	The ``map'' parameter is the location of the content.map file."""
	def __init__(self, map):
		self.f = map
		if(not os.path.isfile(map)):
			open(map, "wb").close()
	def contentByHash(self, hash):
		"""When passed a sha1 hash (string of length 20), this will return the filename of the shared content (/shared1/%08x.app, no NAND prefix) specified by the hash in content.map. Note that if the content is not found, it will return False - not an empty string."""
		cmfp = open(self.f, "rb")
		cmdict = {}
		num = len(cmfp.read()) / 28
		cmfp.seek(0)
		for z in range(num):
			name = cmfp.read(8)
			hash = cmfp.read(20)
			cmdict[name] = hash
		for key, value in cmdict.iteritems():
			if(value == hash):
				return "/shared1/%s.app" % key
		return False #not found

	def addContentToMap(self, contentid, hash):
		"""Adds a content to the content.map file for the contentid and hash.
		Returns the content id."""
		cmfp = open(self.f, "rb")
		cmdict = {}
		num = len(cmfp.read()) / 28
		cmfp.seek(0)
		for z in range(num):
			name = cmfp.read(8)
			hash = cmfp.read(20)
			cmdict[name] = hash
		cmdict["%08x" % contentid] = hash
		cmfp.close()
		cmfp = open(self.f, "wb")
		for key, value in cmdict.iteritems():
			cmfp.write(key)
			cmfp.write(value)
		cmfp.close()
		return contentid

	def addHashToMap(self, hash):
		"""Adds a content to the content.map file for the hash (uses next unavailable content id)
		 Returns the content id."""
		cmfp = open(self.f, "rb")
		cmdict = {}
		cnt = 0
		num = len(cmfp.read()) / 28
		cmfp.seek(0)
		for z in range(num):
			name = cmfp.read(8)
			hasho = cmfp.read(20)
			cmdict[name] = hasho
			cnt += 1
		cmdict["%08x" % cnt] = hash
		cmfp.close()
		cmfp = open(self.f, "wb")
		for key, value in cmdict.iteritems():
			cmfp.write(key)
			cmfp.write(value)
		cmfp.close()
		return cnt

	def contentCount(self):
		cmfp = open(self.f, "rb")
		cmdict = {}
		cnt = 0
		num = len(cmfp.read()) / 28
		cmfp.seek(0)
		for z in range(num):
			name = cmfp.read(8)
			hash = cmfp.read(20)
			cmdict[name] = hash
			cnt += 1
		cmfp.close()
		return cnt

	def contentHashes(self, count):
		cmfp = open(self.f, "rb")
		num = len(cmfp.read()) / 28
		if(num > count):
			num = count
		cmfp.seek(0)
		hashout = ""
		for z in range(num):
			name = cmfp.read(8)
			hashout += cmfp.read(20)
		cmfp.close()
		return hashout

class uidsys:
	"""This class performs all uid.sys related actions. It includes functions to add titles and find titles from the uid.sys file.
	The ``uid'' parameter is the location of the uid.sys file."""
	class UIDSYSStruct(Struct):
		__endian__ = Struct.BE
		def __format__(self):
			self.titleid = Struct.uint64
			self.padding = Struct.uint16
			self.uid = Struct.uint16

	def __init__(self, uid):
		self.f = uid
		if(not os.path.isfile(uid)):
			uidfp = open(uid, "wb")
			uiddat = self.UIDSYSStruct()
			uiddat.titleid = 0x0000000100000002
			uiddat.padding = 0
			uiddat.uid = 0x1000
			uidfp.write(uiddat.pack())
			uidfp.close()
		if((os.path.isfile(uid)) and (len(open(uid, "rb").read()) == 0)):
			uidfp = open(uid, "wb")
			uiddat = self.UIDSYSStruct()
			uiddat.titleid = 0x0000000100000002
			uiddat.padding = 0
			uiddat.uid = 0x1000
			uidfp.write(uiddat.pack())
			uidfp.close()

	def getUIDForTitle(self, title):
		uidfp = open(self.f, "rb")
		uiddat = uidfp.read()
		cnt = len(uiddat) / 12
		uidfp.seek(0)
		uidstr = self.UIDSYSStruct()
		uidict = {}
		for i in range(cnt):
			uidstr.titleid = uidfp.read(8)
			uidstr.padding = uidfp.read(2)
			uidstr.uid = uidfp.read(2)
			uidict[uidstr.titleid] = uidstr.uid
		for key, value in uidict.iteritems():
			if(hexdump(key, "") == ("%016X" % title)):
				return value
		return self.addTitle(title)

	def getTitle(self, uid):
		uidfp = open(self.f, "rb")
		uiddat = uidfp.read()
		cnt = len(uiddat) / 12
		uidfp.seek(0)
		uidstr = self.UIDSYSStruct()
		uidict = {}
		for i in range(cnt):
			uidstr.titleid = uidfp.read(8)
			uidstr.padding = uidfp.read(2)
			uidstr.uid = uidfp.read(2)
			uidict[uidstr.titleid] = uidstr.uid
		for key, value in uidict.iteritems():
			if(hexdump(value, "") == ("%04X" % uid)):
				return key
		return None

	def addTitle(self, title):
		uidfp = open(self.f, "rb")
		uiddat = uidfp.read()
		cnt = len(uiddat) / 12
		uidfp.seek(0)
		uidstr = self.UIDSYSStruct()
		uidict = {}
		enduid = "\x10\x01"
		for i in range(cnt):
			uidstr.titleid = uidfp.read(8)
			uidstr.padding = uidfp.read(2)
			uidstr.uid = uidfp.read(2)
			if(hexdump(uidstr.titleid, "") == ("%016X" % title)):
				uidfp.close()
				return uidstr.uid
			if(struct.unpack(">H", uidstr.uid) >= struct.unpack(">H", enduid)):
				enduid = a2b_hex("%04X" % (struct.unpack(">H", uidstr.uid)[0] + 1))
			uidict[uidstr.titleid] = uidstr.uid
		uidict[a2b_hex("%016X" % title)] = enduid
		uidfp.close()
		uidfp = open(self.f, "wb")
		for key, value in uidict.iteritems():
			uidfp.write(key)
			uidfp.write("\0\0")
			uidfp.write(value)
		uidfp.close()
		return enduid

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

	def __init__(self, f, nand = False):
		self.f = f
		if(not os.path.isfile(f)):
			if(nand != False):
				nand.newFile("/title/00000001/00000002/data/iplsave.bin", "rw----", 0x0001, 0x0000000100000002)
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
			self.updateMD5()

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

	def slotUsed(self, x, y, page):
		"""Returns whether or not the slot at (x,y) on page ``page'' is used."""
		if((x + (y * 4) + (page * 12)) >= 0x30):
			print "Too far!"
			return None
		fp = open(self.f, "rb")
		data = fp.read()
		fp.seek(16 + ((x + (y * 4) + (page * 12))) * 16)
		baseipl_ent = self.IPLSAVE_Entry
		baseipl_ent.type1 = fp.read(1)
		baseipl_ent.type2 = fp.read(1)
		baseipl_ent.unk = fp.read(4)
		baseipl_ent.flags = fp.read(2)
		baseipl_ent.titleid = fp.read(8)
		fp.close()
		if(baseipl_ent.type1 == "\0"):
			return 0
		return baseipl_ent.titleid

	def addTitleBase(self, x, y, page, tid, movable, type, overwrite, clear, isdisc):
		"""A base addTitle function that is used by others. Don't use this."""
		if((x + (y * 4) + (page * 12)) >= 0x30):
			print "Too far!"
			return None
		fp = open(self.f, "rb")
		data = fp.read()
		fp.seek(16 + ((x + (y * 4) + (page * 12))) * 16)
		baseipl_ent = self.IPLSAVE_Entry
		baseipl_ent.type1 = fp.read(1)
		fp.close()
		if((self.slotUsed(x, y, page)) and (not overwrite)):
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
