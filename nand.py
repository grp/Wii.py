import os, hashlib, struct, subprocess, fnmatch, shutil, urllib, array
import wx
import png

from Crypto.Cipher import AES
from Struct import Struct

from common import *
from title import *


class NAND:
	"""This class performs all NAND related things. It includes functions to copy a title (given the TMD) into the correct structure as the Wii does, and will eventually have an entire ES-like system. Parameter f to the initializer is the folder that will be used as the NAND root."""
	def __init__(self, f):
		self.f = f
		self.ES = ESClass(self)
		if(not os.path.isdir(f)):
			os.mkdir(f)
		if(not os.path.isdir(f + "/import")):
			os.mkdir(f + "/import")
		if(not os.path.isdir(f + "/meta")):
			os.mkdir(f + "/meta")
		if(not os.path.isdir(f + "/shared1")):
			os.mkdir(f + "/shared1")
		if(not os.path.isfile(f + "/shared1/content.map")):
			open(f + "/shared1/content.map", "wb").close()
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
		if(not os.path.isfile(f + "/sys/uid.sys")):
			open(f + "/sys/uid.sys", "wb").close()
		if(not os.path.isdir(f + "/ticket")):
			os.mkdir(f + "/ticket")
		if(not os.path.isdir(f + "/title")):
			os.mkdir(f + "/title")
		if(not os.path.isdir(f + "/tmp")):
			os.mkdir(f + "/tmp")
	def contentByHash(self, hash):
		"""When passed a sha1 hash (string of length 20), this will return the path name (including the NAND FS prefix) to the shared content specified by the hash in content.map. Note that if the content is not found, it will return False - not an empty string."""
		cmfp = open(self.f + "/shared1/content.map", "rb")
		cmdict = {}
		num = len(data) / 28
		for z in range(num):
			name = cmfp.read(8)
			hash = cmfp.read(20)
			cmdict[name] = hash
		for key, value in cmdict.iteritems():
			if(value == hash):
				return self.f + "/shared1/%s.app" % key
		return False #not found
	def addContentToMap(self, contentid, hash):
		"""Adds a content to the content.map file for the contentid and hash.
		Returns the content id."""
		cmfp = open(self.f + "/shared1/content.map", "rb")
		cmdict = {}
		num = len(cmfp.read()) / 28
		cmfp.seek(0)
		for z in range(num):
			name = cmfp.read(8)
			hash = cmfp.read(20)
			cmdict[name] = hash
		cmdict["%08x" % contentid] = hash
		cmfp.close()
		cmfp = open(self.f + "/shared1/content.map", "wb")
		for key, value in cmdict.iteritems():
			cmfp.write(key)
			cmfp.write(value)
		cmfp.close()
		return contentid
	def addHashToMap(self, hash):
		"""Adds a content to the content.map file for the hash (uses next unavailable content id)
		 Returns the content id."""
		cmfp = open(self.f + "/shared1/content.map", "rb")
		cmdict = {}
		cnt = 0
		num = len(cmfp.read()) / 28
		cmfp.seek(0)
		for z in range(num):
			name = cmfp.read(8)
			hasho = cmfp.read(20)
			cmdict[name] = hasho
			cnt += 1
		cmdict["%08x" % cnt] = hash
		cmfp.close()
		cmfp = open(self.f + "/shared1/content.map", "wb")
		for key, value in cmdict.iteritems():
			cmfp.write(key)
			cmfp.write(value)
		cmfp.close()
		return cnt
	def importTitle(self, prefix, tmd, tik, is_decrypted = False, result_decrypted = False):
		"""When passed a prefix (the directory to obtain the .app files from, sorted by content id), a TMD instance, and a Ticket instance, this will add that title to the NAND base folder specified in the constructor. Unless is_decrypted is set, the contents are assumed to be encrypted. If result_decrypted is True, then the contents will not end up decrypted."""
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
	def GetNumSharedContents(self):
		"""Gets how many shared contents exist on the NAND"""
		cmfp = open(self.f + "/shared1/content.map", "rb")
		cmdict = {}
		cnt = 0
		num = len(cmfp.read()) / 28
		cmfp.seek(0)
		for z in range(num):
			name = cmfp.read(8)
			hash = cmfp.read(20)
			cmdict[name] = hash
			cnt += 1
		cmfp.close()
		return cnt
	def GetSharedContents(self, cnt):
		"""Gets cnt amount of shared content hashes"""
		cmfp = open(self.f + "/shared1/content.map", "rb")
		num = len(cmfp.read()) / 28
		cmfp.seek(0)
		hashout = ""
		for z in range(num):
			name = cmfp.read(8)
			hashout += cmfp.read(20)
		cmfp.close()
		return hashout
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
		if(self.tmdadded and self.use_version):
			tmd.rawdump(self.f + "/title/%08x/%08x/content/title.tmd.%d" % (self.wtitleid >> 32, self.wtitleid & 0xFFFFFFFF, tmd.tmd.title_version))
		elif(self.tmdadded):
			tmd.rawdump(self.f + "/title/%08x/%08x/content/title.tmd" % (self.wtitleid >> 32, self.wtitleid & 0xFFFFFFFF))
		if(self.ticketadded):
			tik.rawdump(self.f + "/ticket/%08x/%08x.tik" % (self.wtitleid >> 32, self.wtitleid & 0xFFFFFFFF))
		self.AddTitleCancel()
		return 0
