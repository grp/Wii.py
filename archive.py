from common import *
import zlib


class U8(WiiArchive):
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
		strings = '\x00'
		data = ''
		
		for item, value in self.files:
			node = self.U8Node()
			
			recursion = item.count('/')
			if(recursion < 0):
				recursion = 0
			name = item[item.rfind('/') + 1:]
			
			node.name_offset = len(strings)
			strings += name + '\x00'
		
			if(value == None): # directory
				node.type = 0x0100
				node.data_offset = recursion
				
				node.size = len(nodes) + 1
				for one, two in self.files:
					if(one[:len(item)] == item): # find nodes in the folder
						node.size += 1
			else: # file
				node.type = 0x0000
				node.data_offset = len(data)
				#print "before: " + str(len(data))
				data += value + ('\x00' * (align(len(value), 32) - len(value))) # 32 seems to work best for fuzzyness? I'm still really not sure
				#print "after: " + str(len(data))
				node.size = len(value)
				#print "sz: " + str(len(value))
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
		for node in nodes:
			fd += node.pack()
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
		
		for i in range(len(data)):
			header = self.U8Header()
			header.unpack(data[offset:offset + len(header)])
			if(header.tag == "U\xAA8-"):
				break
			data = data[1:]
		offset += len(header)
		offset = header.rootnode_offset
		
		#print header.rootnode_offset
		#print header.header_size
		#print header.data_offset
		
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
				
				#print "Dir: " + name
			elif(node.type == 0): # file
				self.files.append(('/'.join(recursiondir) + '/' + name, data[node.data_offset:node.data_offset + node.size]))
				offset += node.size
				
				#print "File: " + name
			else: # unknown type -- wtf?
				pass
			
			#print "Data Offset: " + str(node.data_offset)
			#print "Size: " + str(node.size)	
			#print "Name Offset: " + str(node.name_offset)
			#print ""
			
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
		


class CCF:
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
