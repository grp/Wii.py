import os, hashlib, struct, subprocess, fnmatch, shutil, urllib, array
from binascii import *

from Crypto.Cipher import AES
from Struct import Struct
from struct import *

from common import *
from title import *
from formats import *


class NAND:
	"""This class performs all NAND related things. It includes functions to copy a title (given the TMD) into the correct structure as the Wii does, and has an entire ES-like system. Parameter f to the initializer is the folder that will be used as the NAND root."""
	def __init__(self, f):
		self.f = f
		if(not os.path.isdir(f)):
			os.mkdir(f)
		if(not os.path.isdir(f + "/import")):
			os.mkdir(f + "/import")
		if(not os.path.isdir(f + "/meta")):
			os.mkdir(f + "/meta")
		if(not os.path.isdir(f + "/shared1")):
			os.mkdir(f + "/shared1")
		if(not os.path.isdir(f + "/shared2")):
			os.mkdir(f + "/shared2")
		if(not os.path.isdir(f + "/sys")):
			os.mkdir(f + "/sys")
		if(not os.path.isfile(f + "/sys/cc.sys")):
			open(f + "/sys/cc.sys", "wb").close()
		if(not os.path.isfile(f + "/sys/cert.sys")):
			open(f + "/sys/cert.sys", "wb").close()
		if(not os.path.isfile(f + "/sys/space.sys")):
			open(f + "/sys/space.sys", "wb").close()
		if(not os.path.isdir(f + "/ticket")):
			os.mkdir(f + "/ticket")
		if(not os.path.isdir(f + "/title")):
			os.mkdir(f + "/title")
		if(not os.path.isdir(f + "/tmp")):
			os.mkdir(f + "/tmp")
		self.ES = ESClass(self)
		self.ISFS = ISFSClass(self)
		self.UID = uidsys(self.f + "/sys/uid.sys")
		self.contentmap = ContentMap(self.f + "/shared1/content.map")

	def getContentByHashFromContentMap(self, hash):
		"""Gets the filename of a shared content with SHA1 hash ``hash''. This includes the NAND prefix."""
		return self.f + self.contentmap.contentByHash(hash)

	def addContentToContentMap(self, contentid, hash):
		"""Adds a content with content ID ``contentid'' and SHA1 hash ``hash'' to the content.map."""
		return self.contentmap.addContentToMap(contentid, hash)

	def addHashToContentMap(self, hash):
		"""Adds a content with SHA1 hash ``hash'' to the content.map. It returns the content ID used."""
		return self.contentmap.addHashToMap(hash)

	def getContentCountFromContentMap(self):
		"""Returns the number of contents in the content.map."""
		return self.contentmap.contentCount()

	def getContentHashesFromContentMap(self, count):
		"""Returns the hashes of ``count'' contents in the content.map."""
		return self.contentmap.contentHashes(count)

	def addTitleToUIDSYS(self, title):
		"""Adds the title with title ID ``title'' to the uid.sys file."""
		return self.UID.addTitle(title)

	def getTitleFromUIDSYS(self, uid):
		"""Gets the title ID with UID ``uid'' from the uid.sys file."""
		return self.UID.getTitle(uid)

	def getUIDForTitleFromUIDSYS(self, title):
		"""Gets the UID for title ID ``title'' from the uid.sys file."""
		return self.UID.getUIDForTitle(uid)

	def addTitleToMenu(self, tid):
		"""Adds a title to the System Menu."""
		a = iplsave(self.f + "/title/00000001/00000002/data/iplsave.bin")
		type = 0
		if(((tid & 0xFFFFFFFFFFFFFF00) == 0x0001000248414300) or ((tid & 0xFFFFFFFFFFFFFF00) == 0x0001000248414200)):
			type = 1
		a.addTitle(0,0, 0, tid, 1, type)

	def addDiscChannelToMenu(self, x, y, page, movable):
		"""Adds the disc channel to the System Menu."""
		a = iplsave(self.f + "/title/00000001/00000002/data/iplsave.bin")
		a.addDisc(x, y, page, movable)

	def deleteTitleFromMenu(self, tid):
		"""Deletes a title from the System Menu."""
		a = iplsave(self.f + "/title/00000001/00000002/data/iplsave.bin")
		a.deleteTitle(tid)

	def importTitle(self, prefix, tmd, tik, add_to_menu = True, is_decrypted = False, result_decrypted = False):
		"""When passed a prefix (the directory to obtain the .app files from, sorted by content id), a TMD instance, and a Ticket instance, this will add that title to the NAND base folder specified in the constructor. If add_to_menu is True, the title (if neccessary) will be added to the menu. The default is True. Unless is_decrypted is set, the contents are assumed to be encrypted. If result_decrypted is True, then the contents will not end up decrypted."""
		self.ES.AddTitleStart(tmd, None, None, is_decrypted, result_decrypted, use_version = True)
		self.ES.AddTitleTMD(tmd)
		self.ES.AddTicket(tik)
		contents = tmd.getContents()
		for i in range(tmd.tmd.numcontents):
			self.ES.AddContentStart(tmd.tmd.titleid, contents[i].cid)
			fp = open(prefix + "/%08x.app" % contents[i].cid, "rb")
			data = fp.read()
			fp.close()
			self.ES.AddContentData(contents[i].cid, data)
			self.ES.AddContentFinish(contents[i].cid)
		self.ES.AddTitleFinish()
		if(add_to_menu == True):
			if((tmd.tmd.titleid >> 32) != 0x00010008):
				self.addTitleToMenu(tmd.tmd.titleid)

class ISFSClass:
	"""This class contains an interface to the NAND that simulates the permissions system and all other aspects of the ISFS.
	The nand argument to the initializer is a NAND object."""
	def __init__(self, nand):
		self.nand = nand
		self.f = nand.f

class ESClass:
	"""This class performs all services relating to titles installed on the Wii. It is a clone of the libogc ES interface.
	The nand argument to the initializer is a NAND object."""
	def __init__(self, nand):
		self.ticketadded = 0
		self.tmdadded = 0
		self.workingcid = 0
		self.workingcidcnt = 0
		self.nand = nand
		self.f = nand.f
	def getContentIndexFromCID(self, tmd, cid):
		"""Gets the content index from the content id cid referenced to in the TMD instance tmd."""
		for i in range(tmd.tmd.numcontents):
			if(cid == tmd.contents[i].cid):
				return tmd.contents[i].index
		return None
	def GetDataDir(self, titleid):
		"""When passed a titleid, it will get the Titles data directory. If there is no title associated with titleid, it will return None."""
		if(not os.path.isdir(self.f + "/title/%08x/%08x/data" % (titleid >> 32, titleid & 0xFFFFFFFF))):
			return None
		return self.f + "/title/%08x/%08x/data" % (titleid >> 32, titleid & 0xFFFFFFFF)
	def GetStoredTMD(self, titleid, version):
		"""Gets the TMD for the specified titleid and version"""
		if(not os.path.isfile(self.f + "/title/%08x/%08x/content/title.tmd.%d" % (titleid >> 32, titleid & 0xFFFFFFFF, version))):
			return None
		return TMD(self.f + "/title/%08x/%08x/content/title.tmd.%d" % (titleid >> 32, titleid & 0xFFFFFFFF, version))
	def GetTitleContentsCount(self, titleid, version):
		"""Gets the number of contents the title with the specified titleid and version has."""
		tmd = self.GetStoredTMD(titleid, version)
		if(tmd == None):
			return 0
		return tmd.tmd.numcontents
	def GetTitleContents(self, titleid, version, count):
		"""Returns a list of content IDs for title id ``titleid'' and version ``version''. It will return, at maximum, ``count'' entries."""
		tmd = self.GetStoredTMD(titleid, version)
		if(tmd == None):
			return 0
		contents = tmd.getContents()
		out = ""
		for z in range(count):
			out += a2b_hex("%08X" % contents[z].cid)
		return out
	def GetNumSharedContents(self):
		"""Gets how many shared contents exist on the NAND"""
		return self.nand.getContentCountFromContentMap()
	def GetSharedContents(self, cnt):
		"""Gets cnt amount of shared content hashes"""
		return self.nand.getContentHashesFromContentMap(cnt)
	def AddTitleStart(self, tmd, certs, crl, is_decrypted = False, result_decrypted = True, use_version = False):
		if(not os.path.isdir(self.f + "/title/%08x" % (tmd.tmd.titleid >> 32))):
			os.mkdir(self.f + "/title/%08x" % (tmd.tmd.titleid >> 32))
		if(not os.path.isdir(self.f + "/title/%08x/%08x" % (tmd.tmd.titleid >> 32, tmd.tmd.titleid & 0xFFFFFFFF))):
			os.mkdir(self.f + "/title/%08x/%08x" % (tmd.tmd.titleid >> 32, tmd.tmd.titleid & 0xFFFFFFFF))
		if(not os.path.isdir(self.f + "/title/%08x/%08x/content" % (tmd.tmd.titleid >> 32, tmd.tmd.titleid & 0xFFFFFFFF))):
			os.mkdir(self.f + "/title/%08x/%08x/content" % (tmd.tmd.titleid >> 32, tmd.tmd.titleid & 0xFFFFFFFF))
		if(not os.path.isdir(self.f + "/title/%08x/%08x/data" % (tmd.tmd.titleid >> 32, tmd.tmd.titleid & 0xFFFFFFFF))):
			os.mkdir(self.f + "/title/%08x/%08x/data" % (tmd.tmd.titleid >> 32, tmd.tmd.titleid & 0xFFFFFFFF))	
		if(not os.path.isdir(self.f + "/ticket/%08x" % (tmd.tmd.titleid >> 32))):
			os.mkdir(self.f + "/ticket/%08x" % (tmd.tmd.titleid >> 32))
		self.workingcids = array.array('L')
		self.wtitleid = tmd.tmd.titleid
		self.is_decrypted = is_decrypted
		self.result_decrypted = result_decrypted
		self.use_version = use_version
		return
	def AddTicket(self, tik):
		"""Adds ticket to the title being added."""
		tik.rawdump(self.f + "/tmp/title.tik")
		self.ticketadded = 1
	def DeleteTicket(self, tikview):
		"""Deletes the ticket relating to tikview
		(UNIMPLEMENTED!)"""
		return
	def AddTitleTMD(self, tmd):
		"""Adds TMD to the title being added."""
		tmd.rawdump(self.f + "/tmp/title.tmd")
		self.tmdadded = 1
	def AddContentStart(self, titleid, cid):
		"""Starts adding a content with content id cid to the title being added with ID titleid."""
		if((self.workingcid != 0) and (self.workingcid != None)):
			"Trying to start an already existing process"
			return -41
		if(self.tmdadded):
			a = TMD(self.f + "/tmp/title.tmd")
		else:
			a = TMD(self.f + "/title/%08x/%08x/content/title.tmd.%d" % (self.wtitleid >> 32, self.wtitleid & 0xFFFFFFFF, tmd.tmd.title_version))
		x = self.getContentIndexFromCID(a, cid)
		if(x == None):
			"Not a valid Content ID"
			return -43
		self.workingcid = cid
		self.workingfp = open(self.f + "/tmp/%08x.app" % cid, "wb")
		return 0
	def AddContentData(self, cid, data):
		"""Adds data to the content cid being added."""
		if(cid != self.workingcid):
			"Working on the not current CID"
			return -40
		self.workingfp.write(data);
		return 0
	def AddContentFinish(self, cid):
		"""Finishes the content cid being added."""
		if(cid != self.workingcid):
			"Working on the not current CID"
			return -40
		self.workingfp.close()
		self.workingcids.append(cid)
		self.workingcidcnt += 1
		self.workingcid = None
		return 0
	def AddTitleCancel(self):
		"""Cancels adding a title (deletes the tmp files and resets status)."""
		if(self.ticketadded):
			os.remove(self.f + "/tmp/title.tik")
			self.ticketadded = 0
		if(self.tmdadded):
			os.remove(self.f + "/tmp/title.tmd")
			self.tmdadded = 0
		for i in range(self.workingcidcnt):
			os.remove(self.f + "/tmp/%08x.app" % self.workingcids[i])
		self.workingcidcnt = 0
		self.workingcid = None
	def AddTitleFinish(self):
		"""Finishes the adding of a title."""
		if(self.ticketadded):
			tik = Ticket(self.f + "/tmp/title.tik")
		else:
			tik = Ticket(self.f + "/ticket/%08x/%08x.tik" % (self.wtitleid >> 32, self.wtitleid & 0xFFFFFFFF))
		if(self.tmdadded):
			tmd = TMD(self.f + "/tmp/title.tmd")
		contents = tmd.getContents()
		for i in range(self.workingcidcnt):
			idx = self.getContentIndexFromCID(tmd, self.workingcids[i])
			if(idx == None):
				print "Content ID doesn't exist!"
				return -42
			fp = open(self.f + "/tmp/%08x.app" % self.workingcids[i], "rb")
			if(contents[idx].type == 0x0001):
				filestr = self.f + "/title/%08x/%08x/content/%08x.app" % (self.wtitleid >> 32, self.wtitleid & 0xFFFFFFFF, self.workingcids[i])
			elif(contents[idx].type == 0x8001):
				num = self.nand.addHashToMap(contents[idx].hash)
				filestr = self.f + "/shared1/%08x.app" % num
			outfp = open(filestr, "wb")
			data = fp.read()
			titlekey = tik.getTitleKey()
			if(self.is_decrypted):
				tmpdata = data
			else:
				tmpdata = Crypto().DecryptContent(titlekey, contents[idx].index, data)
			if(Crypto().ValidateSHAHash(tmpdata, contents[idx].hash) == 0):
				"Decryption failed! SHA1 mismatch."
				return -44
			if(self.result_decrypted != True):
				if(self.is_decrypted):
					tmpdata = Crypto().EncryptContent(titlekey, contents[idx].index, data)
				else:
					tmpdata = data
					
			fp.close()
			outfp.write(tmpdata)
			outfp.close()
		self.nand.addTitleToUIDSYS(self.wtitleid)
		if(self.tmdadded and self.use_version):
			tmd.rawdump(self.f + "/title/%08x/%08x/content/title.tmd.%d" % (self.wtitleid >> 32, self.wtitleid & 0xFFFFFFFF, tmd.tmd.title_version))
		elif(self.tmdadded):
			tmd.rawdump(self.f + "/title/%08x/%08x/content/title.tmd" % (self.wtitleid >> 32, self.wtitleid & 0xFFFFFFFF))
		if(self.ticketadded):
			tik.rawdump(self.f + "/ticket/%08x/%08x.tik" % (self.wtitleid >> 32, self.wtitleid & 0xFFFFFFFF))
		self.AddTitleCancel()
		return 0
