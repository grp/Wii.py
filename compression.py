import os, hashlib, struct, subprocess, fnmatch, shutil, urllib, array
import wx
import png

from Crypto.Cipher import AES
from Struct import Struct

from common import *


class LZ77():
	class WiiLZ77: #class by marcan
		TYPE_LZ77 = 1
		def __init__(self, file, offset):
			self.file = file
			self.offset = offset
 
			self.file.seek(self.offset)
 
			hdr = struct.unpack("<I",self.file.read(4))[0]
			self.uncompressed_length = hdr>>8
			self.compression_type = hdr>>4 & 0xF
 
			if self.compression_type != self.TYPE_LZ77:
				raise ValueError("Unsupported compression method %d"%self.compression_type)
 
		def uncompress(self):
			dout = ""
 
			self.file.seek(self.offset + 0x4)
 
			while len(dout) < self.uncompressed_length:
				flags = struct.unpack("<B",self.file.read(1))[0]
 
				for i in range(8):
					if flags & 0x80:
						info = struct.unpack(">H",self.file.read(2))[0]
						num = 3 + ((info>>12)&0xF)
						disp = info & 0xFFF
						ptr = len(dout) - (info & 0xFFF) - 1
						for i in range(num):
							dout += dout[ptr]
							ptr+=1
							if len(dout) >= self.uncompressed_length:
								break
					else:
						dout += self.file.read(1)
					flags <<= 1
					if len(dout) >= self.uncompressed_length:
						break
			self.data = dout
			return self.data
	def __init__(self, f):
		self.f = f
	def decompress(self, fn = ""):
		"""This uncompresses a LZ77 compressed file, specified in f in the initializer. It outputs the file in either fn, if it isn't empty, or overwrites the input if it is. Returns the output filename."""
		file = open(self.f, "rb")
 		hdr = file.read(4)
 		if hdr != "LZ77":
 			if(fn == ""):
				return self.f
			else:
				data = open(self.f, "rb").read()
				open(fn, "wb").write(data)
		unc = self.WiiLZ77(file, file.tell())
		data = unc.uncompress()
		file.close()
		
		if(fn != ""):
			open(fn, "wb").write(data)
			return fn
		else:
			open(self.f, "wb").write(data)
			return self.f
	def compress(self, fn = ""):
		"""This will eventually add LZ77 compression to a file. Does nothing for now."""
		if(fn != ""):
			#subprocess.call(["./gbalzss", self.f, fn, "-pack"])
			return fn
		else:
			#subprocess.call(["./gbalzss", self.f, self.f, "-pack"])
			return self.f

