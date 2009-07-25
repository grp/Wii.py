from common import *
from title import *
import zlib

class U8(WiiArchive):
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
	def __init__(self):
		self.files = []
	def _dump(self):
		header = self.U8Header()
		rootnode = self.U8Node()
		
		# constants
		header.tag = "U\xAA8-"
		header.rootnode_offset = 0x20
		header.zeroes = "\x00" * 16
		rootnode.type = 0x0100
		
		nodes = []
		strings = "\x00"
		data = ''
		
		for item, value in self.files:
			node = self.U8Node()
			
			recursion = item.count('/')
			if(recursion < 0):
				recursion = 0
			name = item[item.rfind('/') + 1:]
			
			node.name_offset = len(strings)
			strings += name + '\x00'
		
			if(value == None):
				node.type = 0x0100
				node.data_offset = recursion
				
				node.size = len(nodes)
				for one, two in self.files:
					if(one[:len(item)] == item): # find nodes in the folder
						node.size += 1
				node.size += 1
			else:
				sz = len(value)
				node.data_offset = len(data)
				data += value + "\x00" * (align(sz, 32) - sz) # 32 seems to work best for fuzzyness? I'm still really not sure
				node.size = sz
				node.type = 0x0000
			nodes.append(node)
			
		header.header_size = ((len(nodes) + 1) * len(rootnode)) + len(strings)
		header.data_offset = align(header.header_size + header.rootnode_offset, 64)
		rootnode.size = len(nodes) + 1
		
		for i in range(len(nodes)):
			if(nodes[i].type == 0x0000):
				nodes[i].data_offset += header.data_offset
						
		fd = ''
		fd += header.pack()
		fd += rootnode.pack()
		for nodeobj in nodes:
			fd += nodeobj.pack()
		fd += strings
		fd += "\x00" * (header.data_offset - header.rootnode_offset - header.header_size)
		fd += data
		
		return fd
	def _dumpDir(self, dir):
		if(not os.path.isdir(dir)):
			os.mkdir(dir)
		old = os.getcwd()
		os.chdir(dir)
		for item, data in self.files:
			if(data == None):
				if(not os.path.isdir(item)):
					os.mkdir(item)
			else:
				open(item, "wb").write(data)
		os.chdir(old)
	def _loadDir(self, dir):
		try:
			self._tmpPath += ''
		except:
			self._tmpPath = ''
		old = os.getcwd()
		os.chdir(dir)
		entries = os.listdir(".")
		for entry in entries:
			if(os.path.isdir(entry)):
				self.files.append((self._tmpPath + entry, None))
				self._tmpPath += entry + '/'
				self._loadDir(entry)
			elif(os.path.isfile(entry)):
				data = open(entry, "rb").read()
				self.files.append((self._tmpPath + entry, data))
		os.chdir(old)
		self._tmpPath = self._tmpPath[:self._tmpPath.find('/') + 1]
	def _load(self, data):
		offset = 0
		
		header = self.U8Header()
		header.unpack(data[offset:offset + len(header)])
		offset += len(header)
		
		assert header.tag == "U\xAA8-"
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
		
		recursion = [rootnode.size]
		recursiondir = []
		counter = 0
		for node in nodes:
			counter += 1
			name = strings[node.name_offset:].split('\0', 1)[0]
			
			if(node.type == 0x0100): # folder
				recursion.append(node.size)
				recursiondir.append(name)
				assert len(recursion) == node.data_offset + 2 # haxx
				self.files.append(('/'.join(recursiondir), None))
			elif(node.type == 0): # file
				self.files.append(('/'.join(recursiondir) + '/' + name, data[node.data_offset:node.data_offset + node.size]))
				offset += node.size
			else: # unknown type -- wtf?
				pass
								
			sz = recursion.pop()
			if(sz != counter + 1):
				recursion.append(sz)
			else:
				recursiondir.pop()
	def __str__(self):
		ret = ''
		for key, value in self.files:
			name = key[key.rfind('/') + 1:]
			recursion = key.count('/')
			ret += '  ' * recursion
			if(value == None):
				ret += '[' + name + ']'
			else:
				ret += name
			ret += '\n'
		return ret
	def __getitem__(self, key):
		for item, val in self.files:
			if(item == key):
				if(val != None):
					return val
				else:
					ret = []
					for item2, val2 in self.files:
						if(item2.find(item) == 0):
							ret.append(item2[len(item) + 1:])
					return ret[1:]
		raise KeyError
	def __setitem__(self, key, val):
		for i in range(len(self.files)):
			if(self.files[i][0] == key):
				self.files[i] = (self.files[i][0], val)
				return
		self.files.append((key, val))
		

class WAD(WiiArchive):
	def __init__(self, boot2 = False):
		self.tmd = TMD()
		self.tik = Ticket()
		self.contents = []
		self.boot2 = False
		self.cert = ""
	def _load(self, data):
		if(self.boot2 != True):
			headersize, wadtype, certsize, reserved, tiksize, tmdsize, datasize, footersize, padding = struct.unpack('>I4s6I32s', data[:64])
			pos = 64
		else:
			headersize, data_offset, certsize, tiksize, tmdsize, padding = struct.unpack('>IIIII12s', data[:32])
			pos = 32
			
		rawcert = data[pos:pos + certsize]
		pos += certsize
		if(self.boot2 != True):
			if(certsize % 64 != 0):
				pos += 64 - (certsize % 64)
		self.cert = rawcert

		rawtik = data[pos:pos + tiksize]
		pos += tiksize
		if(self.boot2 != True):
			if(tiksize % 64 != 0):
				pos += 64 - (tiksize % 64)
		self.tik = Ticket.load(rawtik)
				
		rawtmd = data[pos:pos + tmdsize]
		pos += tmdsize
		if(self.boot2 == True):
			pos = data_offset
		else:
			pos += 64 - (tmdsize % 64)
		self.tmd = TMD.load(rawtmd)
		
		titlekey = self.tik.getTitleKey()
		contents = self.tmd.getContents()
		for i in range(0, len(contents)):
			tmpsize = contents[i].size
			if(tmpsize % 16 != 0):
				tmpsize += 16 - (tmpsize % 16)
			encdata = data[pos:pos + tmpsize]
			pos += tmpsize
			decdata = Crypto().decryptContent(titlekey, contents[i].index, encdata)
			self.contents.append(decdata)
			if(tmpsize % 64 != 0):
				pos += 64 - (tmpsize % 64)
	def _loadDir(self, dir):
		origdir = os.getcwd()
		os.chdir(dir)
		
		self.tmd = TMD.loadFile("tmd")
		self.tik = Ticket.loadFile("tik")
		self.cert = open("cert", "rb").read()
		
		contents = self.tmd.getContents()
		for i in range(len(contents)):
			self.contents.append(open("%08x.app" % i, "rb").read())
		os.chdir(origdir)
	def _dumpDir(self, dir):
		origdir = os.getcwd()
		os.chdir(dir)
		
		contents = self.tmd.getContents()
		for i in range(len(contents)):
			open("%08x.app" % i, "wb").write(self.contents[i])
		self.tmd.dumpFile("tmd")
		self.tik.dumpFile("tik")
		open("cert", "wb").write(self.cert)
			
		os.chdir(origdir)
	def _dump(self, fakesign = True):
		titlekey = self.tik.getTitleKey()
		contents = self.tmd.getContents()
		
		apppack = ""
		for i, content in enumerate(contents):
			if(fakesign):
				content.hash = str(Crypto().createSHAHash(self.contents[content.index]))
				content.size = len(self.contents[content.index])
			
			encdata = Crypto().encryptContent(titlekey, content.index, self.contents[content.index])
			
			apppack += encdata
			if(len(encdata) % 64 != 0):
				apppack += "\x00" * (64 - (len(encdata) % 64))
					
		if(fakesign):
			self.tmd.setContents(contents)
			self.tmd.fakesign()
			self.tik.fakesign()
		
		rawtmd = self.tmd.dump()
		rawcert = self.cert
		rawtik = self.tik.dump()
		
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
		return pack
	def __getitem__(self, idx):
		return self.contents[idx]
	def __setitem__(self, idx, value):
		self.contents[idx] = value
	def __str__(self):
		out = ""
		out += "Wii WAD:\n"
		out += str(self.tmd)
		out += str(self.tik)		
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

if(__name__ == '__main__'):
	wad = WAD.loadFile("testing.wad")
	print wad
	wad.dumpDir("outdir")
	wad.dumpFile("interesting.wad", fakesign = False) #keyword arguements work as expected when calling _dump(). awesome.
	wad2 = WAD.loadDir("outdir")
	print wad2
	wad3 = WAD.loadFile("interesting.wad")
	print wad3
	wad3.dumpDir("outdir2")
