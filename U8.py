import os, hashlib, struct, subprocess, fnmatch, shutil, urllib, array
import wx
import png

from Crypto.Cipher import AES
from Struct import Struct

from common import *


class U8():
	"""This class can unpack and pack U8 archives, which are used all over the Wii. They are often used in Banners and contents in Downloadable Titles. Please remove all headers and compression first, kthx.
	
	The f parameter is either the source folder to pack, or the source file to unpack."""
	class U8Header(Struct):
		__endian__ = Struct.BE
		def __format__(self):
			self.tag = Struct.string(4)
			self.rootnode_offset = Struct.uint32
			self.header_size = Struct.uint32
			self.data_offset = Struct.uint32
			self.zeroes = Struct.string(16)
	class U8Node(Struct):
		__endian__ = Struct.BE
		def __format__(self):
			self.type = Struct.uint16
			self.name_offset = Struct.uint16
			self.data_offset = Struct.uint32
			self.size = Struct.uint32
	def __init__(self, f):
		self.f = f
	def _pack(self, file, recursion, is_root = 0): #internal
		node = self.U8Node()
		node.name_offset = len(self.strings)
		if(is_root != 1):
			self.strings += (file)
			self.strings += ("\x00")
		
		if(os.path.isdir(file)):
			node.type = 0x0100
			node.data_offset = recursion - 1
			recursion += 1
			files = sorted(os.listdir(file))
			#if(sorted(files) == ["banner.bin", "icon.bin", "sound.bin"]):
			#	files = ["icon.bin", "banner.bin", "sound.bin"]
				
			oldsz = len(self.nodes)
			if(is_root != 1):
				self.nodes.append(node)
			
			os.chdir(file)
			for entry in files:
				if(entry != ".DS_Store" and entry[len(entry) - 4:] != "_out"):
					self._pack(entry, recursion)
			os.chdir("..")

			self.nodes[oldsz].size = len(self.nodes) + 1
		else:
			f = open(file, "rb")
			data = f.read()
			f.close()
			sz = len(data)
			data += "\x00" * (align(sz, 32) - sz) #32 seems to work best for fuzzyness? I'm still really not sure
			node.data_offset = len(self.data)
			self.data += data
			node.size = sz
			node.type = 0x0000
			if(is_root != 1):
				self.nodes.append(node)
				
	def pack(self, fn = ""):
		"""This function will pack a folder into a U8 archive. The output file name is specified in the parameter fn. If fn is an empty string, the filename is deduced from the input folder name. Returns the output filename.
		
		This creates valid U8 archives for all purposes."""
		header = self.U8Header()
		rootnode = self.U8Node()
		
		header.tag = "U\xAA8-"
		header.rootnode_offset = 0x20
		header.zeroes = "\x00" * 16
		
		self.nodes = []
		self.strings = "\x00"
		self.data = ""
		origdir = os.getcwd()
		os.chdir(self.f)
		self._pack(".", 0, 1)
		os.chdir(origdir)
		
		header.header_size = (len(self.nodes) + 1) * len(rootnode) + len(self.strings)
		header.data_offset = align(header.header_size + header.rootnode_offset, 64)
		rootnode.size = len(self.nodes) + 1
		rootnode.type = 0x0100
		
		for i in range(len(self.nodes)):
			if(self.nodes[i].type == 0x0000):
				self.nodes[i].data_offset += header.data_offset
			
		if(fn == ""):
			if(self.f[len(self.f) - 4:] == "_out"):
				fn = os.path.dirname(self.f) + "/" + os.path.basename(self.f)[:-4].replace("_", ".")
			else:
				fn = self.f
			
		fd = open(fn, "wb")
		fd.write(header.pack())
		fd.write(rootnode.pack())
		for node in self.nodes:
			fd.write(node.pack())
		fd.write(self.strings)
		fd.write("\x00" * (header.data_offset - header.rootnode_offset - header.header_size))
		fd.write(self.data)
		fd.close()
		
		return fn
		
	def unpack(self, fn = ""):
		"""This will unpack the U8 archive specified by the initialization parameter into either the folder specified by the parameter fn, or into a folder created with this formula:
		``filename_extension_out``
		
		This will recreate the directory structure, including the initial root folder in the U8 archive (such as "arc" or "meta"). Returns the output directory name."""
		data = open(self.f, "rb").read()
		
		offset = 0
		
		header = self.U8Header()
		header.unpack(data[offset:offset + len(header)])
		offset += len(header)
		
		if(header.tag != "U\xAA8-"):
			raise NameError("Bad U8 Tag")
		offset = header.rootnode_offset
		
		rootnode = self.U8Node()
		rootnode.unpack(data[offset:offset + len(rootnode)])
		offset += len(rootnode)
		
		nodes = []
		for i in range(rootnode.size - 1):
			node = self.U8Node()
			node.unpack(data[offset:offset + len(node)])
			offset += len(node)
			nodes.append(node)
		
		strings = data[offset:offset + header.data_offset - len(header) - (len(rootnode) * rootnode.size)]
		offset += len(strings)
		
		if(fn == ""):
			fn = os.path.dirname(self.f) + "/" + os.path.basename(self.f).replace(".", "_") + "_out"
		try:
			origdir = os.getcwd()
			os.mkdir(fn)
		except:
			pass
		os.chdir(fn)
		
		recursion = [rootnode.size]
		counter = 0
		for node in nodes:
			counter += 1
			name = strings[node.name_offset:].split('\0', 1)[0]
			
			if(node.type == 0x0100): #folder
				recursion.append(node.size)
				try:
					os.mkdir(name)
				except:
					pass
				os.chdir(name)
				continue
			elif(node.type == 0): #file
				file = open(name, "wb")
				file.write(data[node.data_offset:node.data_offset + node.size])
				offset += node.size
			else: #unknown
				pass #ignore
				
			sz = recursion.pop()
			if(sz == counter + 1):
				os.chdir("..")
			else:
				recursion.append(sz)
		os.chdir("..")
		
		os.chdir(origdir)
		return fn
	def __str__(self):
		data = open(self.f, "rb").read()
		
		offset = 0
		
		header = self.U8Header()
		header.unpack(data[offset:offset + len(header)])
		offset += len(header)
		
		if(header.tag != "U\xAA8-"):
			raise NameError("Bad U8 Tag")
		offset = header.rootnode_offset
		
		rootnode = self.U8Node()
		rootnode.unpack(data[offset:offset + len(rootnode)])
		offset += len(rootnode)
		
		nodes = []
		for i in xrange(rootnode.size - 1):
			node = self.U8Node()
			node.unpack(data[offset:offset + len(node)])
			offset += len(node)
			nodes.append(node)
		
		strings = data[offset:offset + header.data_offset - len(header) - (len(rootnode) * rootnode.size)]
		offset += len(strings)
		
		out = "[root]\n"
		recursion = [rootnode.size]
		counter = 0
		for node in nodes:
			counter += 1
			name = strings[node.name_offset:].split('\0', 1)[0]
			out += "  " * len(recursion)
			if(node.type == 0x0100): #folder
				recursion.append(node.size)
				out += "[%s]\n" % name
				continue
			elif(node.type == 0): #file
				out += "%s\n" % name
				offset += node.size
			else: #unknown, ignore
				pass
				
			sz = recursion.pop()
			if(sz == counter + 1):
				pass
			else:
				recursion.append(sz)
		return out
		
class IMD5():
	"""This class can add and remove IMD5 headers to files. The parameter f is the file to use for the addition or removal of the header. IMD5 headers are found in banner.bin, icon.bin, and sound.bin."""
	class IMD5Header(Struct):
		__endian__ = Struct.BE
		def __format__(self):
			self.tag = Struct.string(4)
			self.size = Struct.uint32
			self.zeroes = Struct.uint8[8]
			self.crypto = Struct.string(16)
	def __init__(self, f):
		self.f = f
	def add(self, fn = ""):
		"""This function adds an IMD5 header to the file specified by f in the initializer. The output file is specified with fn, if it is empty, it will overwrite the input file. If the file already has an IMD5 header, it will now have two. Returns the output filename."""
		data = open(self.f, "rb").read()
		
		imd5 = self.IMD5Header()
		for i in range(8):
			imd5.zeroes[i] = 0x00
		imd5.tag = "IMD5"
		imd5.size = len(data)
		imd5.crypto = str(hashlib.md5(data).digest())
		data = imd5.pack() + data
		
		if(fn != ""):
			open(fn, "wb").write(data)
			return fn
		else:
			open(self.f, "wb").write(data)
			return self.f
	def remove(self, fn = ""):
		"""This will remove an IMD5 header from the file specified in f, if one exists. If there is no IMD5 header, it will output the file as it is. It will output in the parameter fn if available, otherwise it will overwrite the source. Returns the output filename."""
		data = open(self.f, "rb").read()
		imd5 = self.IMD5Header()
		if(data[:4] != "IMD5"):
				if(fn != ""):
					open(fn, "wb").write(data) 
					return fn
				else:
					return self.f
		data = data[len(imd5):]
		
		if(fn != ""):
			open(fn, "wb").write(data)
			return fn
		else:
			open(self.f, "wb").write(data)
			return self.f
		
class IMET():
	"""IMET headers are found in Opening.bnr and 0000000.app files. They contain the channel titles and more metadata about channels. They are in two different formats with different amounts of padding before the start of the IMET header. This class suports both.
	
	The parameter f is used to specify the input file name."""
	class IMETHeader(Struct):
		__endian__ = Struct.BE
		def __format__(self):
			self.zeroes = Struct.uint8[128]
			self.tag = Struct.string(4)
			self.unk = Struct.uint64
			self.sizes = Struct.uint32[3] #icon, banner, sound
			self.unk2 = Struct.uint32
			self.names = Struct.string(84, encoding = "utf-16-be", stripNulls = True)[7]
			self.zeroes2 = Struct.uint8[840]
			self.hash = Struct.string(16)
	def __init__(self, f):
		self.f = f
	def add(self, iconsz, bannersz, soundsz, name = "", langs = [], fn = ""):
		"""This function adds an IMET header to the file specified with f in the initializer. The file will be output to fn if it is not empty, otherwise it will overwrite the input file. You must specify the size of banner.bin in bannersz, and respectivly for iconsz and soundsz. langs is an optional arguement that is a list of different langauge channel titles. name is the english name that is copied everywhere in langs that there is an empty string. Returns the output filename."""
		data = open(self.f, "rb").read()
		imet = self.IMETHeader()
		
		for i in imet.zeroes:
			imet.zeroes[i] = 0x00
		imet.tag = "IMET"
		imet.unk = 0x0000060000000003
		imet.sizes[0] = iconsz
		imet.sizes[1] = bannersz
		imet.sizes[2] = soundsz
		imet.unk2 = 0
		for i in range(len(imet.names)):
			if(len(langs) > 0 and langs[i] != ""):
				imet.names[i] = langs[i]
			else:
				imet.names[i] = name
		for i in imet.zeroes2:
			imet.zeroes2[i] = 0x00
		imet.hash = "\x00" * 16
		
		tmp = imet.pack()
		imet.hash = hashlib.md5(tmp[0x40:0x640]).digest() #0x00 or 0x40?
		
		data = imet.pack() + data
		
		if(fn != ""):
			open(fn, "wb").write(data)
			return fn
		else:
			open(self.f, "wb").write(data)
			return self.f
		
	def remove(self, fn = ""):
		"""This method removes an IMET header from a file specified with f in the initializer. fn is the output file name if it isn't an empty string, if it is, it will overwrite the input. If the input has no IMD5 header, it is output as is. Returns the output filename."""
		data = open(self.f, "rb").read()
		if(data[0x80:0x84] == "IMET"):
			data = data[0x640:]
		elif(data[0x40:0x44] == "IMET"):
			data = data[0x640:]
		else:
			if(fn != ""):
				open(fn, "wb").write(data)
				return fn
			else:
				return self.f
		if(fn != ""):
			open(fn, "wb").write(data)
			return fn
		else:
			open(self.f, "wb").write(data)
			return self.f
	def getTitle(self):
		imet = self.IMETHeader()
		data = open(self.f, "rb").read()

		if(data[0x40:0x44] == "IMET"):
			pass
		elif(data[0x80:0x84] == "IMET"):
			data = data[0x40:]
		else:
			return ""

		imet.unpack(data[:len(imet)])
		name = imet.names[1]
		topop = []
		for i in range(len(name)):
			if(name[i] == "\x00"):
				topop.append(i)
		name = list(name)
		popped = 0 #don't ask me why I did this
		for pop in topop:
			name.pop(pop - popped)
			popped += 1	
		
		name = ''.join(name)
		return name
