from common import *
		
class IMD5(WiiHeader):
	class IMD5Header(Struct):
		__endian__ = Struct.BE
		def __format__(self):
			self.tag = Struct.string(4)
			self.size = Struct.uint32
			self.zeroes = Struct.string(8)
			self.crypto = Struct.string(16)
	def add(self):
		imd5 = self.IMD5Header()
		imd5.tag = "IMD5"
		imd5.size = len(self.data)
		imd5.zeroes = '\x00' * 8
		imd5.crypto = str(Crypto.createMD5Hash(self.data))
		self.data = imd5.pack() + self.data
		return self.data
	def remove(self):
		imd5 = self.IMD5Header()
		if(self.data[:4] != "IMD5"):
			return self.data
		self.data = self.data[len(imd5):]
		return self.data
		
class IMET(WiiHeader):
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
	def add(self, iconsz, bannersz, soundsz, name = '', langs = []):
		imet = self.IMETHeader()
		for i in range(len(imet.zeroes)):
			imet.zeroes[i] = 0x00
		imet.tag = 'IMET'
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
		for i in range(len(imet.zeroes2)):
			imet.zeroes2[i] = 0x00
		imet.hash = '\x00' * 16
		tmp = imet.pack()
		imet.hash = Crypto.createMD5Hash(tmp[0x40:0x640])
		self.data = imet.pack() + self.data
		print "testing %x %x %x %x %x" % (len(imet), 128, 840, 0x1A << 1, 84)
		return self.data
	def remove(self):
		data = self.data
		if(data[0x80:0x84] == 'IMET'):
			data = data[0x640:]
		elif(data[0x40:0x44] == 'IMET'):
			data = data[0x640:]
		return data
	def getTitle(self):
		imet = self.IMETHeader()
		data = self.data
		if(data[0x40:0x44] == 'IMET'):
			pass
		elif(data[0x80:0x84] == 'IMET'):
			data = data[0x40:]
		else:
			raise ValueError("No IMET header found!")
		imet.unpack(data[:len(imet)])
		name = imet.names[1]
		topop = []
		for i in range(len(name)):
			if(name[i] == '\x00'):
				topop.append(i)
		name = list(name)
		popped = 0 #don't ask me why I did this
		for pop in topop:
			name.pop(pop - popped)
			popped += 1	
		name = ''.join(name)
		return name
