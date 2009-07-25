import os, hashlib, struct, subprocess, fnmatch, shutil, urllib, array, time, sys, tempfile, wave
from cStringIO import StringIO

from Crypto.Cipher import AES
from PIL import Image

from Struct import Struct

def align(x, boundary):
	if(x % boundary):
		x += (x + boundary) - (x % boundary)
	return x
	
def clamp(var, min, max):
	if var < min: var = min
	if var > max: var = max
	return var

def abs(var):
	if var < 0:
		var = var + (2 * var)
	return var

def hexdump(s, sep=" "): # just dumps hex values
        return sep.join(map(lambda x: "%02x" % ord(x), s))
		
def hexdump2(src, length = 16): # dumps to a "hex editor" style output
	result = []
	for i in xrange(0, len(src), length):
		s = src[i:i + length]
		if(len(s) % 4 == 0):
			mod = 0 
		else: 
			mod = 1 
		hexa = ''
		for j in range((len(s) / 4) + mod):
			hexa += ' '.join(["%02X" % ord(x) for x in s[j * 4:j * 4 + 4]])
			if(j != ((len(s) / 4) + mod) - 1):
				hexa += '  '
		printable = s.translate(''.join([(len(repr(chr(x))) == 3) and chr(x) or '.' for x in range(256)]))
		result.append("0x%04X   %-*s   %s\n" % (i, (length * 3) + 2, hexa, printable))
	return ''.join(result)
	
print hexdump2("RANDOM STRING \x01 TESTING \x214 TEST OF STrasneljkasdhfleasdklhglkaje;shadlkghehaosehlgasdlkfhe;lakhsdglhaelksejdfffffffjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjasdfsadf")

class Crypto(object):
	"""This is a Cryptographic/hash class used to abstract away things (to make changes easier)"""
	align = 64
	@classmethod
	def decryptData(self, key, iv, data, align = True):
		"""Decrypts some data (aligns to 64 bytes, if needed)."""
		if((len(data) % self.align) != 0 and align):
			return AES.new(key, AES.MODE_CBC, iv).decrypt(data + ("\x00" * (self.align - (len(data) % self.align))))
		else:
			return AES.new(key, AES.MODE_CBC, iv).decrypt(data)
	@classmethod
	def encryptData(self, key, iv, data, align = True):
		"""Encrypts some data (aligns to 64 bytes, if needed)."""
		if((len(data) % self.align) != 0 and align):
			return AES.new(key, AES.MODE_CBC, iv).encrypt(data + ("\x00" * (self.align - (len(data) % self.align))))
		else:
			return AES.new(key, AES.MODE_CBC, iv).encrypt(data)
	@classmethod
	def decryptContent(self, titlekey, idx, data):
		"""Decrypts a Content."""
		iv = struct.pack(">H", idx) + "\x00" * 14
		return self.decryptData(titlekey, iv, data)
	@classmethod
	def decryptTitleKey(self, commonkey, tid, enckey):
		"""Decrypts a Content."""
		iv = struct.pack(">Q", tid) + "\x00" * 8
		return self.decryptData(commonkey, iv, enckey, False)
	@classmethod
	def encryptContent(self, titlekey, idx, data):
		"""Encrypts a Content."""
		iv = struct.pack(">H", idx) + "\x00" * 14
		return self.encryptData(titlekey, iv, data)
	@classmethod
	def createSHAHash(self, data): #tested WORKING (without padding)
		return hashlib.sha1(data).digest()
	@classmethod
	def createSHAHashHex(self, data):
		return hashlib.sha1(data).hexdigest()
	@classmethod
	def createMD5HashHex(self, data):
		return hashlib.md5(data).hexdigest()
	@classmethod
	def createMD5Hash(self, data):
		return hashlib.md5(data).digest()
	@classmethod
	def validateSHAHash(self, data, hash):
		contentHash = hashlib.sha1(data).digest()
		return 1
		if (contentHash == hash):
			return 1
		else:
			#raise ValueError('Content hash : %s : len %i' % (hexdump(contentHash), len(contentHash)) + 'Expected : %s : len %i' % (hexdump(hash), len(hash)))
			return 0

class WiiObject(object):
	@classmethod
	def load(cls, data, *args, **kwargs):
		self = cls()
		self._load(data, *args, **kwargs)
		return self
	@classmethod
	def loadFile(cls, filename, *args, **kwargs):
		return cls.load(open(filename, "rb").read(), *args, **kwargs)
	
	def dump(self, *args, **kwargs):
		return self._dump(*args, **kwargs)
	def dumpFile(self, filename, *args, **kwargs):
		open(filename, "wb").write(self.dump(*args, **kwargs))
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

class WiiHeader(object):
	def __init__(self, data):
		self.data = data
	def addFile(self, filename):
		open(filename, "wb").write(self.add())
	def removeFile(self, filename):
		open(filename, "wb").write(self.remove())
	@classmethod
	def loadFile(cls, filename, *args, **kwargs):
		return cls(open(filename, "rb").read(), *args, **kwargs)
	
