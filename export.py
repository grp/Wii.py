from common import *
from title import *
from image import *

class Savegame():
	class savegameHeader(Struct):
		__endian__ = Struct.BE
		def __format__(self):
			self.savegameId = Struct.uint32[2]
			self.bannerSize = Struct.uint32
			self.permissions = Struct.uint8
			self.unknown1 = Struct.uint8
			self.md5hash = Struct.string(16)
			self.unknown2 = Struct.uint16
			
	class savegameBanner(Struct):
		__endian__ = Struct.BE
		def __format__(self):
			self.magic = Struct.string(4)
			self.reserved = Struct.uint8[4]
			self.flags = Struct.uint32
			self.reserved = Struct.uint32[5]
			self.gameTitle = Struct.string(64)
			self.gameSubTitle = Struct.string(64)
			self.banner = Struct.string(24576)
			self.icon0 = Struct.string(4608)
			self.icon1 = Struct.string(4608)
			self.icon2 = Struct.string(4608)
			self.icon3 = Struct.string(4608)
			self.icon4 = Struct.string(4608)
			self.icon5 = Struct.string(4608)
			self.icon6 = Struct.string(4608)
			self.icon7 = Struct.string(4608)
			
	class backupHeader(Struct):
		__endian__ = Struct.BE
		def __format__(self):
			self.hdrSize = Struct.uint32
			self.magic = Struct.string(2)
			self.version = Struct.uint16
			self.NGid = Struct.uint32
			self.filesCount = Struct.uint32
			self.filesSize = Struct.uint32
			self.unknown1 = Struct.uint32
			self.unknown2 = Struct.uint32
			self.totalSize = Struct.uint32
			self.unknown3 = Struct.uint8[64]
			self.unknown4 = Struct.uint32
			self.gameId = Struct.string(4)
			self.wiiMacAddr = Struct.uint8[6]
			self.unknown6 = Struct.uint16
			self.padding = Struct.uint32[4]	
			
	class fileHeader(Struct):
		__endian__ = Struct.BE
		def __format__(self):
			self.magic = Struct.uint32
			self.size = Struct.uint32
			self.permissions = Struct.uint8
			self.attribute = Struct.uint8
			self.type = Struct.uint8
			self.nameIV = Struct.string(0x45)
			
	def __init__(self, f):
		self.f = f
		try:
			self.fd = open(f, 'r+b')
		except:
			raise Exception('Cannot open input')
		
		self.sdKey = '\xab\x01\xb9\xd8\xe1\x62\x2b\x08\xaf\xba\xd8\x4d\xbf\xc2\xa5\x5d'
		self.sdIv = '\x21\x67\x12\xe6\xaa\x1f\x68\x9f\x95\xc5\xa2\x23\x24\xdc\x6a\x98'
		
		self.iconCount = 1
		
	def __str__(self):
		ret = ''
		ret += '\nSavegame header \n'
		
		ret += 'Savegame ID : 0x%x%x\n' % (self.hdr.savegameId[0], self.hdr.savegameId[1])
		ret += 'Banner size : 0x%x\n' % self.hdr.bannerSize
		ret += 'Permissions : 0x%x\n' % self.hdr.permissions
		ret += 'Unknown : 0x%x\n' % self.hdr.unknown1
		ret += 'MD5 hash : %s\n' % hexdump(self.hdr.md5hash)
		ret += 'Unknown : 0x%x\n' % self.hdr.unknown2
		
		ret += '\nBanner header \n'
		
		ret += 'Flags : 0x%x\n' % self.bnr.flags
		ret += 'Game title : %s\n' % self.bnr.gameTitle
		ret += 'Game subtitle : %s\n' % self.bnr.gameSubTitle
		ret += 'Icons found : %i\n' % self.iconCount
		
		ret += '\nBackup header \n'	
		
		ret += 'Header size : 0x%x (+ 0x10 of padding) version 0x%x\n' % (self.bkHdr.hdrSize, self.bkHdr.version)
		if self.bkHdr.gameId[3] == 'P':
			ret += 'Region : PAL\n'
		elif self.bkHdr.gameId[3] == 'E':
			ret += 'Region : NTSC\n'
		elif self.bkHdr.gameId[3] == 'J':
			ret += 'Region : JAP\n'
		ret += 'Game ID : %s\n' % self.bkHdr.gameId
		ret += 'Wii unique ID : 0x%x\n' % self.bkHdr.NGid
		ret += 'Wii MAC address %02x:%02x:%02x:%02x:%02x:%02x\n' % (self.bkHdr.wiiMacAddr[0], self.bkHdr.wiiMacAddr[1], self.bkHdr.wiiMacAddr[2], self.bkHdr.wiiMacAddr[3], self.bkHdr.wiiMacAddr[4], self.bkHdr.wiiMacAddr[5])
		ret += 'Found %i files for %i bytes\n' % (self.bkHdr.filesCount, self.bkHdr.filesSize)
		ret += 'Total size : %i bytes\n' % self.bkHdr.totalSize
		ret += 'This save is %i blocks wise' % (self.bkHdr.totalSize / 0x20000)
		
		return ret
		
	def extractFiles(self):

		try:
			os.mkdir(os.path.dirname(self.f) + '/' + self.bkHdr.gameId)
		except:
			pass
			
		os.chdir(os.path.dirname(self.f) + '/' + self.bkHdr.gameId)
		
		self.fd.seek(self.fileStartOffset)
		
		for i in range(self.bkHdr.filesCount):
			
			fileHdr = self.fd.read(0x80)
			fileHdr = self.fileHeader().unpack(fileHdr)
			
			if fileHdr.magic != 0x03adf17e:
				raise Exception('Wrong file magic')
				
			fileHdr.size = align(fileHdr.size, 64)
			
			ivpos = 0
			name = ""
			i = 0
			for char in list(fileHdr.nameIV):
				if(char == "\x00"):
					i -= 1
					ivpos = i
					break
				else:
					name += char
				i += 1

					
			fileIV = fileHdr.nameIV[ivpos:ivpos + 16]

			if len(fileIV) != 16:
				raise Exception('IV alignment issue')
			
			if fileHdr.type == 1:
				print 'Extracted %s (%ib)' % (name, fileHdr.size)
				
				fileBuffer = self.fd.read(fileHdr.size)
				fileBuffer = Crypto().decryptData(self.sdKey, fileIV, fileBuffer, True)
				try:
					open(name, 'w+b').write(fileBuffer)
				except:
					raise Exception('Cannot write the output')
			elif fileHdr.type == 2:
				print 'Extracted folder %s' % name
				try:
					os.mkdir(name)
				except:
					pass
					
			print 'Attribute %i Permission %i' % (fileHdr.attribute, fileHdr.permissions)
			print 'File IV : 0x%s' % hexdump(fileIV, '')
			
		os.chdir('..')
		
	def analyzeHeader(self):
		headerBuffer = self.fd.read(0xF0C0)
		headerBuffer = Crypto().decryptData(self.sdKey, self.sdIv, headerBuffer, True)

		self.hdr = self.savegameHeader().unpack(headerBuffer[:0x20])
		
		#headerBuffer.replace(self.hdr.md5hash, '\x0e\x65\x37\x81\x99\xbe\x45\x17\xab\x06\xec\x22\x45\x1a\x57\x93')
		#print 'Reashed md5 : %s' % hexdump(Crypto().createMD5Hash(headerBuffer))
		
		self.bnr = self.savegameBanner().unpack(headerBuffer[0x20:])
		
		if self.bnr.magic != 'WIBN':
			raise Exception ('Wrong magic, should be WIBN')
		
		if self.hdr.bannerSize != 0x72A0:
			self.iconCount += 7	
		
		bkHdrBuffer = self.fd.read(0x80)
		self.bkHdr = self.backupHeader().unpack(bkHdrBuffer)
		
		if self.bkHdr.magic != 'Bk' or self.bkHdr.hdrSize != 0x70:
			raise Exception ('Bk header error')
			
		self.fileStartOffset = self.fd.tell()
		
	def eraseWiiMac(self):
		self.fd.seek(0xF128)
		print self.fd.write('\x00' * 6)		
	
	def getBanner(self):
		try:
			os.mkdir(os.path.dirname(self.f) + '/' + self.bkHdr.gameId)
		except:
			pass
			
		os.chdir(os.path.dirname(self.f) + '/' + self.bkHdr.gameId)		
		
		return Image.fromstring("RGBA", (192, 64), TPL('').RGB5A3((192, 64), self.bnr.banner)).save('banner', 'png')
		
	def getIcon(self, index):
		if index < 0 or index > 7 or index > self.iconCount:
			return -1
			
		try:
			os.mkdir(os.path.dirname(self.f) + '/' + self.bkHdr.gameId)
		except:
			pass
			
		os.chdir(os.path.dirname(self.f) + '/' + self.bkHdr.gameId)			
			
		if index == 0:
			return Image.fromstring("RGBA", (48, 48), TPL('').RGB5A3((48, 48), self.bnr.icon0)).save('icon' + str(index), 'png')
		if index == 1:
			return Image.fromstring("RGBA", (48, 48), TPL('').RGB5A3((48, 48), self.bnr.icon1)).save('icon' + str(index), 'png')
		if index == 2:
			return Image.fromstring("RGBA", (48, 48), TPL('').RGB5A3((48, 48), self.bnr.icon2)).save('icon' + str(index), 'png')
		if index == 3:
			return Image.fromstring("RGBA", (48, 48), TPL('').RGB5A3((48, 48), self.bnr.icon3)).save('icon' + str(index), 'png')
		if index == 4:
			return Image.fromstring("RGBA", (48, 48), TPL('').RGB5A3((48, 48), self.bnr.icon4)).save('icon' + str(index), 'png')
		if index == 5:
			return Image.fromstring("RGBA", (48, 48), TPL('').RGB5A3((48, 48), self.bnr.icon5)).save('icon' + str(index), 'png')
		if index == 6:
			return Image.fromstring("RGBA", (48, 48), TPL('').RGB5A3((48, 48), self.bnr.icon6)).save('icon' + str(index), 'png')
		if index == 7:
			return Image.fromstring("RGBA", (48, 48), TPL('').RGB5A3((48, 48), self.bnr.icon7)).save('icon' + str(index), 'png')
		
	def getIconsCount(self):
		return self.iconCount
		
	def getSaveString(self, string):
		if string == 'id':
			return self.bkHdr.gameId
		elif string == 'title':
			return self.bnr.gameTitle
		elif string == 'subtitle':
			return self.bnr.gameSubTitle
		elif string == 'mac':
			return self.bkHdr.wiiMacAddr[0] + ':' + self.bkHdr.wiiMacAddr[1] + ':' + self.bkHdr.wiiMacAddr[2] + ':' + self.bkHdr.wiiMacAddr[3] + ':' + self.bkHdr.wiiMacAddr[4] + ':' + self.bkHdr.wiiMacAddr[5]
			
	def getFilesCount(self):
		return self.bkHdr.filesCount
