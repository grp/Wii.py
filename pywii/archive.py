from common import *
from title import *
import zlib

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

class WAD:
	"""This class is to pack and unpack WAD files, which store a single title. You pass the input filename or input directory name to the parameter f.
	
	WAD packing support currently creates WAD files that return -4100 on install."""
	def __init__(self, f, boot2 = False):
		self.f = f
		self.boot2 = boot2
	def pack(self, fn = "", fakesign = True, decrypted = True):
		"""Packs a WAD into the filename specified by fn, if it is not empty. If it is empty, it packs into a filename generated from the folder's name. If fakesign is True, it will fakesign the Ticket and TMD, and update them as needed. If decrypted is true, it will assume the contents are already decrypted. For now, fakesign can not be True if decrypted is False, however fakesign can be False if decrypted is True. Title ID is a long integer of the destination title id."""
		os.chdir(self.f)
		
		tik = Ticket().loadFile("tik")
		tmd = TMD().loadFile("tmd")
		titlekey = tik.getTitleKey()
		contents = tmd.getContents()
		
		apppack = ""
		for content in contents:
			tmpdata = open("%08x.app" % content.index, "rb").read()
			
			if(decrypted):
				if(fakesign):
					content.hash = str(Crypto().createSHAHash(tmpdata))
					content.size = len(tmpdata)
			
				encdata = Crypto().encryptContent(titlekey, content.index, tmpdata)
			else:
				encdata = tmpdata
			
			apppack += encdata
			if(len(encdata) % 64 != 0):
				apppack += "\x00" * (64 - (len(encdata) % 64))
					
		if(fakesign):
			tmd.setContents(contents)
			tmd.dump()
			tik.dump()
		
		rawtmd = open("tmd", "rb").read()
		rawcert = open("cert", "rb").read()
		rawtik = open("tik", "rb").read()
		
		sz = 0
		for i in range(len(contents)):
			sz += contents[i].size
			if(sz % 64 != 0):
				sz += 64 - (contents[i].size % 64)
		
		if(self.boot2 != True):
			pack = struct.pack('>I4s6I', 32, "Is\x00\x00", len(rawcert), 0, len(rawtik), len(rawtmd), sz, 0)
			pack += "\x00" * 32
		else:
			pack = struct.pack('>IIIII12s', 32, align(len(rawcert) + len(rawtik) + len(rawtmd), 0x40), len(rawcert), len(rawtik), len(rawtmd), "\x00" * 12)
		
		pack += rawcert
		if(len(rawcert) % 64 != 0 and self.boot2 != True):
			pack += "\x00" * (64 - (len(rawcert) % 64))
		pack += rawtik
		if(len(rawtik) % 64 != 0 and self.boot2 != True):
			pack += "\x00" * (64 - (len(rawtik) % 64))
		pack += rawtmd
		if(len(rawtmd) % 64 != 0 and self.boot2 != True):
			pack += "\x00" * (64 - (len(rawtmd) % 64))
		
		if(self.boot2 == True):
			pack += "\x00" * (align(len(rawcert) + len(rawtik) + len(rawtmd), 0x40) - (len(rawcert) + len(rawtik) + len(rawtmd)))
		
		pack += apppack
		
		os.chdir('..')
		if(fn == ""):
			if(self.f[len(self.f) - 4:] == "_out"):
				fn = os.path.dirname(self.f) + "/" + os.path.basename(self.f)[:len(os.path.basename(self.f)) - 4].replace("_", ".")
			else:
				fn = self.f
		open(fn, "wb").write(pack)
		return fn
	def unpack(self, fn = ""):
		"""Unpacks the WAD from the parameter f in the initializer to either the value of fn, if there is one, or a folder created with this formula: `filename_extension_out`. Certs are put in the file "cert", TMD in the file "tmd", ticket in the file "tik", and contents are put in the files based on index and with ".app" added to the end."""
		fd = open(self.f, 'rb')
		if(self.boot2 != True):
			headersize, wadtype, certsize, reserved, tiksize, tmdsize, datasize, footersize, padding= struct.unpack('>I4s6I32s', fd.read(64))
		else:
			headersize, data_offset, certsize, tiksize, tmdsize, padding = struct.unpack('>IIIII12s', fd.read(32))
		
		try:
			if(fn == ""):
				fn = self.f.replace(".", "_") + "_out"
			os.mkdir(fn)
		except OSError:
			pass
		os.chdir(fn)
		
		rawcert = fd.read(certsize)
		if(self.boot2 != True):
			if(certsize % 64 != 0):
				fd.seek(64 - (certsize % 64), 1)
		open('cert', 'wb').write(rawcert)

		rawtik = fd.read(tiksize)
		if(self.boot2 != True):
			if(tiksize % 64 != 0):
				fd.seek(64 - (tiksize % 64), 1)
		open('tik', 'wb').write(rawtik)
				
		rawtmd = fd.read(tmdsize)
		if(self.boot2 == True):
			fd.seek(data_offset)
		else:
			fd.seek(64 - (tmdsize % 64), 1)
		open('tmd', 'wb').write(rawtmd)
		
		titlekey = Ticket().loadFile("tik").getTitleKey()
		contents = TMD().loadFile("tmd").getContents()
		for i in range(0, len(contents)):
			tmpsize = contents[i].size
			if(tmpsize % 16 != 0):
				tmpsize += 16 - (tmpsize % 16)
			tmptmpdata = fd.read(tmpsize)
			tmpdata = Crypto().decryptContent(titlekey, contents[i].index, tmptmpdata)
			open("%08x.app" % contents[i].index, "wb").write(tmpdata)
			if(tmpsize % 64 != 0):
				fd.seek(64 - (tmpsize % 64), 1)
		fd.close()
		os.chdir('..')
		
		return fn
	def __str__(self):
		out = ""
		out += "Wii WAD:\n"
		fd = open(self.f, 'rb')
		
		if(self.boot2 != True):
			headersize, wadtype, certsize, reserved, tiksize, tmdsize, datasize, footersize, padding= struct.unpack('>I4s6I32s', fd.read(64))
		else:
			headersize, data_offset, certsize, tiksize, tmdsize, padding = struct.unpack('>IIIII12s', fd.read(32))
		
		rawcert = fd.read(certsize)
		if(certsize % 64 != 0):
			fd.seek(64 - (certsize % 64), 1)
		rawtik = fd.read(tiksize)
		if(self.boot2 != True):
			if(tiksize % 64 != 0):
				fd.seek(64 - (tiksize % 64), 1)		
		rawtmd = fd.read(tmdsize)
		
		if(self.boot2 != True):
			out += " Header %02x Type '%s' Certs %x Tiket %x TMD %x Data %x Footer %x\n" % (headersize, wadtype, certsize, tiksize, tmdsize, datasize, footersize)
		else:
			out += " Header %02x Type 'boot2' Certs %x Tiket %x TMD %x Data @ %x\n" % (headersize, certsize, tiksize, tmdsize, data_offset)
		
		out += str(Ticket().load(rawtik))
		out += str(TMD().load(rawtmd))
		
		return out


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
		