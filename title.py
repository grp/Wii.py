from common import *

class TicketView:
	"""Creates a ticket view from the Ticket object ``tik''."""
	class TikviewStruct(Struct):
		__endian__ = Struct.BE
		def __format__(self):
			self.view = Struct.uint32
			self.ticketid = Struct.uint64
			self.devicetype = Struct.uint32
			self.titleid = Struct.uint64
			self.accessmask = Struct.uint16
			self.reserved = Struct.string(0x3C)
			self.cidxmask = Struct.string(0x40)
			self.padding = Struct.uint16
			self.limits = Struct.string(96)

	def __init__(self, tik):
		self.tikview = self.TikviewStruct()
		self.tikview.view = 0
		self.tikview.ticketid = tik.tik.tikid
		self.tikview.devicetype = tik.tik.console
		self.tikview.titleid = tik.getTitleID()
		self.tikview.accessmask = 0xFFFF	# This needs to be changed, I'm sure...
		self.tikview.reserved = "\0" * 0x3C
		self.tikview.cidxmask = "\xFF" * 0x40	# This needs to be changed, I'm sure...
		self.tikview.padding = 0x0000
		self.tikview.limits = "\0" * 96

	def __str__(self):
		out = ""
		out += " Ticket View:\n"
		out += "  Title ID: %08X-%08X\n" % (self.tikview.titleid >> 32, self.tikview.titleid & 0xFFFFFFFF)
		out += "  Device type: %08X\n" % self.tikview.devicetype
		out += "  Ticket ID: %016X\n" % self.tikview.ticketid
		out += "  Access Mask: %04X\n" % self.tikview.accessmask
		
		return out

class Ticket(WiiObject):	
	"""Creates a ticket from the filename defined in f. This may take a longer amount of time than expected, as it also decrypts the title key. Now supports Korean tickets (but their title keys stay Korean on dump)."""
	class TicketStruct(Struct):
		__endian__ = Struct.BE
		def __format__(self):
			self.rsaexp = Struct.uint32
			self.rsamod = Struct.string(256)
			self.padding1 = Struct.string(60)
			self.rsaid = Struct.string(64)
			self.padding2 = Struct.string(63)
			self.enctitlekey = Struct.string(16)
			self.unk1 = Struct.uint8
			self.tikid = Struct.uint64
			self.console = Struct.uint32
			self.titleid = Struct.uint64
			self.unk2 = Struct.uint16
			self.dlc = Struct.uint16
			self.unk3 = Struct.uint64
			self.commonkey_index = Struct.uint8
			self.reserved = Struct.string(80)
			self.unk3 = Struct.uint16
			self.limits = Struct.string(96)
			self.unk4 = Struct.uint8
	def __init__(self):
		self.tik = self.TicketStruct()
		
		self.tik.rsaexp = 0x10001
		self.tik.rsamod = "\x00" * 256
		self.tik.padding1 = "\x00" * 60
		self.tik.rsaid = "\x00" * 64
		self.tik.padding2 = "\x00" * 63
		self.tik.enctitlekey = "\x00" * 16
		self.tik.titleid = 0x0000000100000000
		self.tik.reserved = "\x00" * 80
		self.tik.limits = "\x00" * 96
		
		commonkey = "\xEB\xE4\x2A\x22\x5E\x85\x93\xE4\x48\xD9\xC5\x45\x73\x81\xAA\xF7"
		koreankey = "\x63\xB8\x2B\xB4\xF4\x61\x4E\x2E\x13\xF2\xFE\xFB\xBA\x4C\x9B\x7E"
		
		if(self.tik.commonkey_index == 1): #korean, kekekekek!
			commonkey = koreankey
		self.titlekey = Crypto().decryptTitleKey(commonkey, self.tik.titleid, self.tik.enctitlekey)
	def _load(self, data):
		self.tik.unpack(data[:len(self.tik)])
		
		commonkey = "\xEB\xE4\x2A\x22\x5E\x85\x93\xE4\x48\xD9\xC5\x45\x73\x81\xAA\xF7"
		koreankey = "\x63\xB8\x2B\xB4\xF4\x61\x4E\x2E\x13\xF2\xFE\xFB\xBA\x4C\x9B\x7E"
		
		if(self.tik.commonkey_index == 1): #korean, kekekekek!
			commonkey = koreankey
		
		self.titlekey = Crypto().decryptTitleKey(commonkey, self.tik.titleid, self.tik.enctitlekey)
		return self
	def getTitleKey(self):
		"""Returns a string containing the title key."""
		return self.titlekey
	def getTitleID(self):
		"""Returns a long integer with the title id."""
		return self.tik.titleid
	def setTitleID(self, titleid):
		"""Sets the title id of the ticket from the long integer passed in titleid."""
		self.tik.titleid = titleid
		commonkey = "\xEB\xE4\x2A\x22\x5E\x85\x93\xE4\x48\xD9\xC5\x45\x73\x81\xAA\xF7"
		koreankey = "\x63\xB8\x2B\xB4\xF4\x61\x4E\x2E\x13\xF2\xFE\xFB\xBA\x4C\x9B\x7E"
		
		if(self.tik.commonkey_index == 1): #korean, kekekekek!
			commonkey = koreankey
		self.titlekey = Crypto().decryptTitleKey(commonkey, self.tik.titleid, self.tik.enctitlekey) #This changes the decrypted title key!
	def __str__(self):
		out = ""
		out += " Ticket:\n"
		out += "  Title ID: %08x-%08x\n" % (self.getTitleID() >> 32, self.getTitleID() & 0xFFFFFFFF)
	
		out += "  Title key IV: "
		out += hexdump(struct.pack(">Q", self.getTitleID()) + "\x00\x00\x00\x00\x00\x00\x00\x00")
		out += "\n"
	
		out += "  Title key (encrypted): "
		out += hexdump(self.tik.enctitlekey)
		out += "\n"
	
		out += "  Title key (decrypted): "
		out += hexdump(self.getTitleKey())
		out += "\n"
		
		return out
	def fakesign(self):
		"""Fakesigns (or Trucha signs) and dumps the ticket to either fn, if not empty, or overwriting the source if empty. Returns the output filename."""
		self.rsamod = self.rsamod = "\x00" * 256
		for i in range(65536):
			self.tik.unk2 = i
			if(Crypto().createSHAHashHex(self.tik.pack())[:2] == "00"):
				break
			if(i == 65535):
				raise ValueError("Failed to fakesign. Aborting...")
	def _dump(self):
		"""Dumps the ticket to either fn, if not empty, or overwriting the source if empty. **Does not fakesign.** Returns the output filename."""
		return self.tik.pack()
	def __len__(self):
		return len(self.tik)

class TMD(WiiObject):
	"""This class allows you to edit TMDs. TMD (Title Metadata) files are used in many places to hold information about titles. The parameter f to the initialization is the filename to open and create a TMD from."""
	class TMDContent(Struct):
		__endian__ = Struct.BE
		def __format__(self):
			self.cid = Struct.uint32
			self.index = Struct.uint16
			self.type = Struct.uint16
			self.size = Struct.uint64
			self.hash = Struct.string(20)
	class TMDStruct(Struct):
		__endian__ = Struct.BE
		def __format__(self):
			self.rsaexp = Struct.uint32
			self.rsamod = Struct.string(256)
			self.padding1 = Struct.string(60)
			self.rsaid = Struct.string(64)
			self.version = Struct.uint8[4]
			self.iosversion = Struct.uint64
			self.titleid = Struct.uint64
			self.title_type = Struct.uint32
			self.group_id = Struct.uint16
			self.reserved = Struct.string(62)
			self.access_rights = Struct.uint32
			self.title_version = Struct.uint16
			self.numcontents = Struct.uint16
			self.boot_index = Struct.uint16
			self.padding2 = Struct.uint16
			#contents follow this
	def _load(self, data):
		self.tmd.unpack(data[:len(self.tmd)])
		pos = len(self.tmd)
		for i in range(self.tmd.numcontents):
			cont = self.TMDContent()
			cont.unpack(data[pos:pos + len(cont)])
			pos += len(cont)
			self.contents.append(cont)
	def __init__(self):
		self.tmd = self.TMDStruct()
		self.tmd.titleid = 0x0000000100000000
		self.contents = []
	def getContents(self):
		"""Returns a list of contents. Each content is an object with the members "size", the size of the content's decrypted data; "cid", the content id; "type", the type of the content (0x8001 for shared, 0x0001 for standard, more possible), and a 20 byte string called "hash"."""
		return self.contents
	def setContents(self, contents):
		"""This sets the contents in the TMD to the contents you provide in the contents parameter. Also updates the TMD to the appropraite amount of contents."""
		self.contents = contents
		self.tmd.numcontents = len(contents)
	def __str__(self):
		out = ""
		out += " TMD:\n"
		out += "  Versions: (todo) %u, CA CRL (todo) %u, Signer CRL (todo) %u, System %u-%u\n" % (0, 0, 0, self.getIOSVersion() >> 32, self.getIOSVersion() & 0xFFFFFFFF)
		out += "  Title ID: %08x-%08x\n" % (self.getTitleID() >> 32, self.getTitleID() & 0xFFFFFFFF)
		out += "  Title Type: %u\n" % self.tmd.title_type
		out += "  Group ID: '%02u'\n" % self.tmd.group_id
		out += "  Access Rights: 0x%08x\n" % self.tmd.access_rights
		out += "  Title Version: 0x%04x\n" % self.tmd.title_version
		out += "  Boot Index: %u\n" % self.getBootIndex()
		out += "  Contents: \n"
	
		out += "   ID       Index Type    Size         Hash\n"
		contents = self.getContents()
		for i in range(len(contents)):
			out += "   %08X %-4u  0x%04x  %#-12x " % (contents[i].cid, contents[i].index, contents[i].type, contents[i].size)
			out += hexdump(contents[i].hash)
			out += "\n"
		
		return out
	def __len__(self):
		contents = self.getContents()
		sz = len(self.tmd)
		for i in range(len(contents)):
			sz += len(contents[i])
		return sz
	def fakesign(self):
		"""Dumps the TMD to the filename specified in fn, if not empty. If that is empty, it overwrites the original. This fakesigns the TMD, but does not update the hashes and the sizes, that is left as a job for you. Returns output filename."""
		for i in range(65536):
			self.tmd.padding2 = i
			
			data = "" #gotta reset it every time
			data += self.tmd.pack()
			for i in range(self.tmd.numcontents):
				data += self.contents[i].pack()
			if(Crypto().createSHAHashHex(data)[:2] == "00"):
				break
			if(i == 65535):
				raise ValueError("Failed to fakesign! Aborting...")
	def _dump(self):
		"""Same as the :dump: function, but does not fakesign the TMD. Also returns output filename."""
		data = ""
		data += self.tmd.pack()
		for i in range(self.tmd.numcontents):
			data += self.contents[i].pack()
					
		return data
	def getTitleID(self):
		"""Returns the long integer title id."""
		return self.tmd.titleid
	def setTitleID(self, titleid):
		"""Sets the title id to the long integer specified in the parameter titleid."""
		self.tmd.titleid = titleid
	def getIOSVersion(self):
		"""Returns the IOS version the title will run off of."""
		return self.tmd.iosversion
	def setIOSVersion(self, version):
		"""Sets the IOS version the title will run off of to the arguement version."""
		self.tmd.iosverison = version
	def getBootIndex(self):
		"""Returns the boot index of the TMD."""
		return self.tmd.boot_index
	def setBootIndex(self, index):
		"""Sets the boot index of the TMD to the value of index."""
		self.tmd.boot_index = index

class Title(WiiArchive):
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
	def _dumpDir(self, dir, useidx = True, decrypt = True):
		origdir = os.getcwd()
		if not os.path.isdir(dir):
			os.mkdir(dir)
		os.chdir(dir)
		
		contents = self.tmd.getContents()
		titlekey = self.tik.getTitleKey()
		for i, content  in enumerate(contents):
			if(useidx == True):
				output = content.index
			else:
				output = content.cid
			if(decrypt == True):
				open("%08x.app" % output, "wb").write(self.contents[i][:contents[i].size])
			else:
				open("%08x.app" % output, "wb").write(Crypto.encryptContent(titlekey, content.index, self.contents[content.index]))
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
				content.hash = str(Crypto.createSHAHash(self.contents[content.index]))
				content.size = len(self.contents[content.index])
			
			encdata = Crypto.encryptContent(titlekey, content.index, self.contents[content.index])
			
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
	def fakesign(self):
		self.tik.fakesign()
		self.tmd.fakesign()
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

WAD = Title

class NUS:
	"""This class can download titles from NUS, or Nintendo Update Server. The titleid parameter is the long integer version of the title to download. The version parameter is optional and specifies the version to download. If version is not given, it is assumed to be the latest version on NUS."""
	url = "http://nus.cdn.shop.wii.com/ccs/download/"
	def download(self, titleid, version = None):
		certs = ""
		tmd = TMD.load(urllib.urlopen("http://nus.cdn.shop.wii.com/ccs/download/0000000100000002/tmd.289").read())
		tik = Ticket.load(urllib.urlopen("http://nus.cdn.shop.wii.com/ccs/download/0000000100000002/cetk").read())

		rawtmd = urllib.urlopen("http://nus.cdn.shop.wii.com/ccs/download/0000000100000002/tmd.289").read()
		rawtik = urllib.urlopen("http://nus.cdn.shop.wii.com/ccs/download/0000000100000002/cetk").read()
		certs += rawtik[0x2A4:0x2A4 + 0x300] #XS
		certs += rawtik[0x2A4 + 0x300:] #CA (tik)
		certs += rawtmd[0x328:0x328 + 0x300] #CP

		#certs += tik.dump()[0x2A4:0x2A4 + 0x300] #XS
		#certs += tik.dump()[0x2A4 + 0x300:] #CA (tik)
		#certs += tmd.dump()[0x328:0x328 + 0x300] #CP

		if(Crypto.createMD5HashHex(certs) != "7ff50e2733f7a6be1677b6f6c9b625dd"):
			raise ValueError("Failed to create certs! MD5 mistatch.")
		
		if(version == None):
			versionstring = ""
		else:
			versionstring = ".%u" % version
			
		titleurl = self.url + "%08x%08x/" % (titleid >> 32, titleid & 0xFFFFFFFF)
		
		tmd = TMD.load(urllib.urlopen(titleurl + "tmd" + versionstring).read())
		tik = Ticket.load(urllib.urlopen(titleurl + "cetk").read())
		
		title = Title()
		title.tmd = tmd
		title.tik = tik
		title.cert = certs
		
		contents = tmd.getContents()
		for content in contents:
			encdata = urllib.urlopen(titleurl + ("%08x" % content.cid)).read(content.size)
			decdata = Crypto.decryptContent(tik.titlekey, content.index, encdata)
			if(Crypto.validateSHAHash(decdata, content.hash) == 0):
				raise ValueError("Decryption failed! SHA1 mismatch.")
			title.contents.append(decdata)
		return title
	download = classmethod(download)
