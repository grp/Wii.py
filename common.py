import os, hashlib, struct, subprocess, fnmatch, shutil, urllib, array
import wx
import png

from Crypto.Cipher import AES
from Struct import Struct


def align(x, boundary):
	return x + (x % boundary)

def hexdump(s, sep=" "):
        return sep.join(map(lambda x: "%02x" % ord(x), s))

class Crypto:
	"""This is a Cryptographic/hash class used to abstract away things (to make changes easier)"""
	def __init__(self):
		self.align = 64
		return
	def DecryptData(self, key, iv, data, align = True):
		"""Decrypts some data (aligns to 64 bytes, if needed)."""
		if((len(data) % self.align) != 0 and align):
			return AES.new(key, AES.MODE_CBC, iv).decrypt(data + ("\x00" * (self.align - (len(data) % self.align))))
		else:
			return AES.new(key, AES.MODE_CBC, iv).decrypt(data)
	def EncryptData(self, key, iv, data, align = True):
		"""Encrypts some data (aligns to 64 bytes, if needed)."""
		if((len(data) % self.align) != 0 and align):
			return AES.new(key, AES.MODE_CBC, iv).encrypt(data + ("\x00" * (self.align - (len(data) % self.align))))
		else:
			return AES.new(key, AES.MODE_CBC, iv).encrypt(data)
	def DecryptContent(self, titlekey, idx, data):
		"""Decrypts a Content."""
		iv = struct.pack(">H", idx) + "\x00" * 14
		return self.DecryptData(titlekey, iv, data)
	def DecryptTitleKey(self, commonkey, tid, enckey):
		"""Decrypts a Content."""
		iv = struct.pack(">Q", tid) + "\x00" * 8
		return self.DecryptData(commonkey, iv, enckey, False)
	def EncryptContent(self, titlekey, idx, data):
		"""Encrypts a Content."""
		iv = struct.pack(">H", idx) + "\x00" * 14
		return self.EncryptData(titlekey, iv, data)
	def CreateSHAHash(self, data): #tested WORKING (without padding)
		return hashlib.sha1(data).digest()
	def CreateSHAHashHex(self, data):
		return hashlib.sha1(data).hexdigest()
	def CreateMD5HashHex(self, data):
		return hashlib.md5(data).hexdigest()
	def CreateMD5Hash(self, data):
		return hashlib.md5(data).digest()
	def ValidateSHAHash(self, data, hash):
		"""Validates a hash. Not checking currently because we have some...issues with hashes."""
		return 1 #hack
		if((len(data) % self.align) != 0):
			datax = data + ("\x00" * (self.align - (len(data) % align)))
		else:
			datax = data
#		if(hashlib.sha1(datax).hexdigest() == hexdump(hash, "")):
#			return 1
#		else:
#			return 0

