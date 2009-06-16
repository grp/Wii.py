import os, hashlib, struct, subprocess, fnmatch, shutil, urllib, array
import wx
import png

import zlib
from Crypto.Cipher import AES
from Struct import Struct

from common import *

class CCF():
	class CCFHeader(Struct):
		__endian__ = Struct.LE
		def __format__(self):
			self.magic = Struct.string(4)
			self.zeroes12 = Struct.string(12)
			self.rootOffset = Struct.uint32
			self.filesCount = Struct.uint32
			self.zeroes8 = Struct.string(8)
			
	class CCFFile(Struct):
		__endian__ = Struct.LE
		def __format__(self):
			self.fileName = Struct.string(20)
			self.fileOffset = Struct.uint32
			self.fileSize = Struct.uint32
			self.fileSizeDecompressed = Struct.uint32

	def __init__(self, fileName):
		self.fileName = fileName
		self.fd = open(fileName, 'r+b')
		
	def compress(self, folder):
		fileList = []
		
		fileHdr = self.CCFHeader()
		
		files = os.listdir(folder)
		
		fileHdr.magic = "\x43\x43\x46\x00"
		fileHdr.zeroes12 = '\x00' * 12
		fileHdr.rootOffset = 0x20
		fileHdr.zeroes8 = '\x00' * 8
		
		currentOffset = len(fileHdr)
		packedFiles = 0
		previousFileEndOffset = 0
		
		for file in files:
			if os.path.isdir(folder + '/' + file) or file == '.DS_Store':
				continue
			else:
				fileList.append(file)
				
		fileHdr.filesCount = len(fileList)
		self.fd.write(fileHdr.pack())
		self.fd.write('\x00' * (fileHdr.filesCount * len(self.CCFFile())))
		
		for fileNumber in range(len(fileList)):
			
			fileEntry = self.CCFFile()
			
			compressedBuffer = zlib.compress(open(folder + '/' + fileList[fileNumber]).read())
			
			fileEntry.fileName = fileList[fileNumber]
			fileEntry.fileSize = len(compressedBuffer)
			fileEntry.fileSizeDecompressed = os.stat(folder + '/' + fileList[fileNumber]).st_size
			fileEntry.fileOffset = align(self.fd.tell(), 32) / 32
			
			print 'File {0} ({1}Kb) placed at offset 0x{2:X}'.format(fileEntry.fileName, fileEntry.fileSize / 1024, fileEntry.fileOffset * 32)
	
			self.fd.seek(len(fileHdr) + fileNumber * len(self.CCFFile()))
			self.fd.write(fileEntry.pack())
			self.fd.seek(fileEntry.fileOffset * 32)
			self.fd.write(compressedBuffer)
			
		self.fd.close()		

	def decompress(self):
		fileHdr = self.CCFHeader()
		hdrData = self.fd.read(len(fileHdr))
		fileHdr.unpack(hdrData)
		
		print 'Found {0} file/s and root node at 0x{1:X}'.format(fileHdr.filesCount, fileHdr.rootOffset)
		
		if fileHdr.magic != "\x43\x43\x46\x00":
			raise ValueError("Wrong magic, 0x{0}".format(fileHdr.magic))
			
		try:
			os.mkdir(os.path.dirname(self.fileName) + '/' + self.fd.name.replace(".", "_") + "_out")
		except:
			pass
			
		os.chdir(os.path.dirname(self.fileName) + '/' + self.fd.name.replace(".", "_") + "_out")
		
		currentOffset = len(fileHdr)
		
		for x in range(fileHdr.filesCount):
			self.fd.seek(currentOffset)
			
			fileEntry = self.CCFFile()
			fileData = self.fd.read(len(fileEntry))
			fileEntry.unpack(fileData)
			
			fileEntry.fileOffset = fileEntry.fileOffset * 32
						
			print 'File {0} at offset 0x{1:X}'.format(fileEntry.fileName, fileEntry.fileOffset)
			print 'File size {0}Kb ({1}Kb decompressed)'.format(fileEntry.fileSize / 1024, fileEntry.fileSizeDecompressed / 1024)
			
			output = open(fileEntry.fileName.rstrip('\0'), 'w+b')
			
			self.fd.seek(fileEntry.fileOffset)
			if fileEntry.fileSize == fileEntry.fileSizeDecompressed:
				print 'The file is stored uncompressed'
				output.write(self.fd.read(fileEntry.fileSize))
			else:
				print 'The file is stored compressed..decompressing'
				decompressedBuffer = zlib.decompress(self.fd.read(fileEntry.fileSize))
				output.write(decompressedBuffer)
			output.close()
			
			currentOffset += len(fileEntry)
		
		
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

