import os, struct, subprocess, fnmatch, shutil, urllib, array
import wx
import png

from Struct import Struct

from common import *


class Ticket:	
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
	def __init__(self, f, korean = False):
		isf = False
		try:
			isf = os.path.isfile(f)
		except:
			pass
		if(isf):
			self.f = f
			data = open(f, "rb").read()
		else:
			self.f = "tik"
			data = f
			
		self.size = len(data)
		self.tik = self.TicketStruct()
		self.tik.unpack(data[:len(self.tik)])
		
		commonkey = "\xEB\xE4\x2A\x22\x5E\x85\x93\xE4\x48\xD9\xC5\x45\x73\x81\xAA\xF7"
		koreankey = "\x63\xB8\x2B\xB4\xF4\x61\x4E\x2E\x13\xF2\xFE\xFB\xBA\x4C\x9B\x7E"
		
		if(self.tik.commonkey_index == 1): #korean, kekekekek!
			commonkey = koreankey
		
		self.titlekey = Crypto().DecryptTitleKey(commonkey, self.tik.titleid, self.tik.enctitlekey)
	def getTitleKey(self):
		"""Returns a string containing the title key."""
		return self.titlekey
	def getTitleID(self):
		"""Returns a long integer with the title id."""
		return self.tik.titleid
	def setTitleID(self, titleid):
		"""Sets the title id of the ticket from the long integer passed in titleid."""
		self.tik.titleid = titleid
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
		
	def dump(self, fn = ""):
		"""Fakesigns (or Trucha signs) and dumps the ticket to either fn, if not empty, or overwriting the source if empty. Returns the output filename."""
		self.rsamod = self.rsamod = "\x00" * 256
		for i in range(65536):
			self.tik.unk2 = i
			if(Crypto().CreateSHAHashHex(self.tik.pack())[:2] == "00"):
				break
			if(i == 65535):
				raise ValueError("Failed to fakesign. Aborting...")
			
		if(fn == ""):
			open(self.f, "wb").write(self.tik.pack())
			return self.f
		else:
			open(fn, "wb").write(self.tik.pack())
			return fn
	def rawdump(self, fn = ""):
		"""Dumps the ticket to either fn, if not empty, or overwriting the source if empty. **Does not fakesign.** Returns the output filename."""
		if(fn == ""):
			open(self.f, "wb").write(self.tik.pack())
			return self.f
		else:
			open(fn, "wb").write(self.tik.pack())
			return fn
	def __len__(self):
		return len(self.tik)

class TMD:
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
			
	def __init__(self, f):
		isf = False
		try:
			isf = os.path.isfile(f)
		except:
			pass
		if(isf):
			self.f = f
			data = open(f, "rb").read()
		else:
			self.f = "tmd"
			data = f
		
		self.tmd = self.TMDStruct()
		self.tmd.unpack(data[:len(self.tmd)])
		
		self.contents = []
		pos = len(self.tmd)
		for i in range(self.tmd.numcontents):
			cont = self.TMDContent()
			cont.unpack(data[pos:pos + len(cont)])
			pos += len(cont)
			self.contents.append(cont)
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
	def dump(self, fn = ""):
		"""Dumps the TMD to the filename specified in fn, if not empty. If that is empty, it overwrites the original. This fakesigns the TMD, but does not update the hashes and the sizes, that is left as a job for you. Returns output filename."""
		for i in range(65536):
			self.tmd.padding2 = i
			
			data = "" #gotta reset it every time
			data += self.tmd.pack()
			for i in range(self.tmd.numcontents):
				data += self.contents[i].pack()
			if(Crypto().CreateSHAHashHex(data)[:2] == "00"):
				break
			if(i == 65535):
				raise ValueError("Failed to fakesign! Aborting...")
			
		if(fn == ""):
			open(self.f, "wb").write(data)
			return self.f
		else:
			open(fn, "wb").write(data)
			return fn
	def rawdump(self, fn = ""):
		"""Same as the :dump: function, but does not fakesign the TMD. Also returns output filename."""
		data = ""
		data += self.tmd.pack()
		for i in range(self.tmd.numcontents):
			data += self.contents[i].pack()
					
		if(fn == ""):
			open(self.f, "wb").write(data)
			return self.f
		else:
			open(fn, "wb").write(data)
			return fn
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

class NUS:
	"""This class can download titles from NUS, or Nintendo Update Server. The titleid parameter is the long integer version of the title to download. The version parameter is optional and specifies the version to download. If version is not given, it is assumed to be the latest version on NUS."""
	def __init__(self, titleid, version = None):
		self.titleid = titleid
		self.baseurl = "http://nus.cdn.shop.wii.com/ccs/download/%08x%08x/" % (titleid >> 32, titleid & 0xFFFFFFFF)
		self.version = version
	def download(self, fn = "", decrypt = True, useidx = True):
		"""This will download a title from NUS into a directory either specified by fn (if it is not empty) or a directory created by the title id in hex form. If decrypt is true, it will decrypt the contents, otherwise it will not. A certs file is always created to enable easy WAD Packing. The parameter useidx specifies wheither to use the index or the content id for the file naming (default is index)."""
		if(fn == ""):
			fn = "%08x%08x" % (self.titleid >> 32, self.titleid & 0xFFFFFFFF)
		try:
			os.mkdir(fn)
		except:
			pass
		os.chdir(fn)
		
		certs = ""
		rawtmd = urllib.urlopen("http://nus.cdn.shop.wii.com/ccs/download/0000000100000002/tmd.289").read()
		rawtik = urllib.urlopen("http://nus.cdn.shop.wii.com/ccs/download/0000000100000002/cetk").read()
		
		certs += rawtik[0x2A4:0x2A4 + 0x300] #XS
		certs += rawtik[0x2A4 + 0x300:] #CA (tik)
		certs += rawtmd[0x328:0x328 + 0x300] #CP

		if(Crypto().CreateMD5HashHex(certs) != "7ff50e2733f7a6be1677b6f6c9b625dd"):
			raise ValueError("Failed to create certs! MD5 mistatch.")
		
		open("cert", "wb").write(certs)
		
		if(self.version == None):
			versionstring = ""
		else:
			versionstring = ".%u" % self.version
		
		urllib.urlretrieve(self.baseurl + "tmd" + versionstring, "tmd")
		tmd = TMD("tmd")
		tmd.rawdump("tmd") #this is to strip off the certs, and this won't fakesign so it should work
		
		urllib.urlretrieve(self.baseurl + "cetk", "tik")
		tik = Ticket("tik")
		tik.rawdump("tik") #this is to strip off the certs, and this won't fakesign so it should work
		if(decrypt):
			titlekey = tik.getTitleKey()
		
		contents = tmd.getContents()
		for content in contents:
			output = content.cid
			if(useidx):
				output = content.index
				
			urllib.urlretrieve(self.baseurl + ("%08x" % content.cid), "%08x.app" % output)
			
			if(decrypt):
				data = open("%08x.app" % output, "rb").read(content.size)
				tmpdata = Crypto().DecryptContent(titlekey, content.index, data)
				if(Crypto().ValidateSHAHash(tmpdata, content.hash) == 0):
					raise ValueError("Decryption failed! SHA1 mismatch.")
				open("%08x.app" % output, "wb").write(tmpdata)
				
		os.chdir("..")

class WAD:
	"""This class is to pack and unpack WAD files, which store a single title. You pass the input filename or input directory name to the parameter f.
	
	WAD packing support currently creates WAD files that return -4100 on install."""
	def __init__(self, f, boot2 = False):
		self.f = f
		self.boot2 = boot2
	def pack(self, fn = "", fakesign = True, decrypted = True):
		"""Packs a WAD into the filename specified by fn, if it is not empty. If it is empty, it packs into a filename generated from the folder's name. If fakesign is True, it will fakesign the Ticket and TMD, and update them as needed. If decrypted is true, it will assume the contents are already decrypted. For now, fakesign can not be True if decrypted is False, however fakesign can be False if decrypted is True. Title ID is a long integer of the destination title id."""
		os.chdir(self.f)
		
		tik = Ticket("tik")
		tmd = TMD("tmd")
		titlekey = tik.getTitleKey()
		contents = tmd.getContents()
		
		apppack = ""
		for content in contents:
			tmpdata = open("%08x.app" % content.index, "rb").read()
			
			if(decrypted):
				if(fakesign):
					content.hash = str(Crypto().CreateSHAHash(tmpdata))
					content.size = len(tmpdata)
			
				encdata = Crypto().EncryptContent(titlekey, content.index, tmpdata)
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
		
		titlekey = Ticket("tik").getTitleKey()
		contents = TMD("tmd").getContents()
		for i in range(0, len(contents)):
			tmpsize = contents[i].size
			if(tmpsize % 16 != 0):
				tmpsize += 16 - (tmpsize % 16)
			tmptmpdata = fd.read(tmpsize)
			tmpdata = Crypto().DecryptContent(titlekey, contents[i].index, tmptmpdata)
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
		
		out += str(Ticket(rawtik))
		out += str(TMD(rawtmd))
		
		return out
