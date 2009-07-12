import os, hashlib, struct, subprocess, fnmatch, shutil, urllib, array, time, sys, tempfile

from Crypto.Cipher import AES
from PIL import Image

from Struct import Struct

def align(x, boundary):
	if(x % boundary):
		x += (x + boundary) - (x % boundary)
	return x

def hexdump(s, sep=" "):
        return sep.join(map(lambda x: "%02x" % ord(x), s))

class Crypto:
	"""This is a Cryptographic/hash class used to abstract away things (to make changes easier)"""
	def __init__(self):
		self.align = 64
		return
	def decryptData(self, key, iv, data, align = True):
		"""Decrypts some data (aligns to 64 bytes, if needed)."""
		if((len(data) % self.align) != 0 and align):
			return AES.new(key, AES.MODE_CBC, iv).decrypt(data + ("\x00" * (self.align - (len(data) % self.align))))
		else:
			return AES.new(key, AES.MODE_CBC, iv).decrypt(data)
	def encryptData(self, key, iv, data, align = True):
		"""Encrypts some data (aligns to 64 bytes, if needed)."""
		if((len(data) % self.align) != 0 and align):
			return AES.new(key, AES.MODE_CBC, iv).encrypt(data + ("\x00" * (self.align - (len(data) % self.align))))
		else:
			return AES.new(key, AES.MODE_CBC, iv).encrypt(data)
	def decryptContent(self, titlekey, idx, data):
		"""Decrypts a Content."""
		iv = struct.pack(">H", idx) + "\x00" * 14
		return self.decryptData(titlekey, iv, data)
	def decryptTitleKey(self, commonkey, tid, enckey):
		"""Decrypts a Content."""
		iv = struct.pack(">Q", tid) + "\x00" * 8
		return self.decryptData(commonkey, iv, enckey, False)
	def encryptContent(self, titlekey, idx, data):
		"""Encrypts a Content."""
		iv = struct.pack(">H", idx) + "\x00" * 14
		return self.encryptData(titlekey, iv, data)
	def createSHAHash(self, data): #tested WORKING (without padding)
		return hashlib.sha1(data).digest()
	def createSHAHashHex(self, data):
		return hashlib.sha1(data).hexdigest()
	def createMD5HashHex(self, data):
		return hashlib.md5(data).hexdigest()
	def createMD5Hash(self, data):
		return hashlib.md5(data).digest()
	def validateSHAHash(self, data, hash):
		contentHash = hashlib.sha1(data).digest()
		
		print 'Content hash : %s : len %i' % (hexdump(contentHash), len(contentHash))
		print 'Expected : %s : len %i' % (hexdump(hash), len(hash))
		
		if (contentHash == hash):
			return 1
		else:
			return 0

class WiiObject(object):
	@classmethod
	def load(cls, data):
		self = cls()
		self._load(data)
		return self
	@classmethod
	def loadFile(cls, filename):
		return cls.load(open(filename, "rb").read())
	
	def dump(self):
		return self._dump()
	def dumpFile(self, filename):
		open(filename, "wb").write(self.dump())
		return filename

class WiiArchive(WiiObject):
	@classmethod
	def loadDir(cls, dirname):
		self = cls()
		self._loadDir(dirname)
		return self
		
	def dumpDir(self, dirname):
		if(not os.path.isdir(dirname)):
			os.mkdir(dirname)
		self._dumpDir(dirname)
		return dirname
