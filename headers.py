from common import *
		
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
		imd5.crypto = str(Crypto().createMD5Hash(data))
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
		imet.hash = Crypto().createMD5Hash(tmp[0x40:0x640]) #0x00 or 0x40?
		
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
