from binascii import *
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

		self.perms = f + "/permission.txt"
		if(not os.path.isfile(self.perms)):
			open(self.perms, "wb").close()
		self.newDirectory("/sys", "rwrw--", 0)
		self.newFile("/sys/uid.sys", "rwrw--", 0)
		self.UID = uidsys(self.f + "/sys/uid.sys")
		self.newDirectory("/meta", "rwrwrw", 0x0001, 0x0000000100000002)
		
		self.newDirectory("/import", "rwrw--", 0x0000)
		self.newDirectory("/shared1", "rwrw--", 0x0000)
		self.newDirectory("/shared2", "rwrwrw", 0x0000)
		self.newFile("/sys/cc.sys", "rwrw--", 0x0000)
		self.newFile("/sys/cert.sys", "rwrwr-", 0x0000)
		self.newFile("/sys/space.sys", "rwrw--", 0x0000)
		self.newDirectory("/ticket", "rwrw--", 0x0000)
		self.newDirectory("/title", "rwrwr-", 0x0000)
		self.newDirectory("/tmp", "rwrwrw", 0x0000)
		self.ES = ESClass(self)
		self.ISFS = ISFSClass(self)
		self.ES._setisfs()
		self.ISFS._setes()
		self.contentmap = ContentMap(self.f + "/shared1/content.map")

	def hasPermissionEntry(self, dir):
		pfp = open(self.perms, "rb")
		data = pfp.read()
		pfp.close()
		ret = data.find(dir)
		if(ret == -1):
			return 0
		return 1

	def removePermissionEntry(self, dir):
		pfp = open(self.perms, "rb")
		data = pfp.read()
		pfp.close()
		ret = data.find(dir)
		if(ret == -1):
			return 0
		newlineloc = -1
		for i in range(ret):
			if(data.startswith("\n", i)):
				newlineloc = i + 1
		endloc = data.find("\n", newlineloc)
		pfp = open(self.perms, "rb")
		data = pfp.read(newlineloc)
		pfp.seek(endloc + 1)
		data += pfp.read()
		pfp.close()
		pfp = open(self.perms, "wb")
		pfp.write(data)
		pfp.close()
		return 1

	def _getFilePermissionBase(self, dir, loc):
		pfp = open(self.perms, "rb")
		data = pfp.read()
		pfp.close()
		ret = data.find(dir)
		if(ret == -1):
			return 0
		newlineloc = 0
		for i in range(ret):
			if(data.startswith("\n", i)):
				newlineloc = i + 1
		endloc = data.find("\n", newlineloc)
		pfp = open(self.perms, "rb")
		if(loc > 0):
			loc *= 2
		pfp.seek(newlineloc + 1 + loc)
		pdata = pfp.read(2)
		pfp.close()
		return pdata

	def getFilePermissionOwner(self, dir):
		pdata = self._getFilePermissionBase(dir, 0)
		pval = 0
		if(pdata[0] == "r"):
			pval += 1
		if(pdata[1] == "w"):
			pval += 2
		return pval

	def getFilePermissionGroup(self, dir):
		pdata = self._getFilePermissionBase(dir, 1)
		pval = 0
		if(pdata[0] == "r"):
			pval += 1
		if(pdata[1] == "w"):
			pval += 2
		return pval

	def getFilePermissionOthers(self, dir):
		pdata = self._getFilePermissionBase(dir, 2)
		pval = 0
		if(pdata[0] == "r"):
			pval += 1
		if(pdata[1] == "w"):
			pval += 2
		return pval

	def getFilePermissionPerms(self, dir):
		pfp = open(self.perms, "rb")
		data = pfp.read()
		pfp.close()
		ret = data.find(dir)
		if(ret == -1):
			return 0
		newlineloc = 0
		for i in range(ret):
			if(data.startswith("\n", i)):
				newlineloc = i + 1
		endloc = data.find("\n", newlineloc)
		pfp = open(self.perms, "rb")
		pfp.seek(newlineloc + 1)
		pdata = pfp.read(6)
		pfp.close()
		return pdata

	def _setFilePermissionBase(self, dir, loc, val):
		pfp = open(self.perms, "rb")
		data = pfp.read()
		pfp.close()
		ret = data.find(dir)
		if(ret == -1):
			return 0
		newlineloc = 0
		for i in range(ret):
			if(data.startswith("\n", i)):
				newlineloc = i + 1
		endloc = data.find("\n", newlineloc)
		pfp = open(self.perms, "rb")
		if(loc > 0):
			loc *= 2
		pfp.seek(newlineloc + 1 + loc)
		pfp.write(val)
		pfp.close()

	def setFilePermissionOwner(self, dir, val):
		out = ""
		if(val & 1):
			out += "r"
		if(val & 2):
			out += "w"
		self._setFilePermissionBase(dir, 0, out)

	def setFilePermissionGroup(self, dir):
		out = ""
		if(val & 1):
			out += "r"
		if(val & 2):
			out += "w"
		self._setFilePermissionBase(dir, 1, out)

	def setFilePermissionOthers(self, dir):
		out = ""
		if(val & 1):
			out += "r"
		if(val & 2):
			out += "w"
		self._setFilePermissionBase(dir, 2, out)

	def isFileDirectory(self, dir):
		pdata = self._getFilePermissionBase(dir, -1)
		pval = 0
		if(pdata[0] == "d"):
			pval += 1
		return pval
		

	def getFilePermissionUID(self, dir):
		pfp = open(self.perms, "rb")
		data = pfp.read()
		pfp.close()
		ret = data.find(dir)
		if(ret == -1):
			return 0
		newlineloc = -1
		for i in range(ret):
			if(data.startswith("\n", i)):
				newlineloc = i + 1
		endloc = data.find("\n", newlineloc)
		pfp = open(self.perms, "rb")
		pfp.seek(newlineloc + 8)
		uidata = pfp.read(4)
		pfp.close()
		return int(uidata, 16)

	def getFilePermissionGID(self, dir):
		pfp = open(self.perms, "rb")
		data = pfp.read()
		pfp.close()
		ret = data.find(dir)
		if(ret == -1):
			return 0
		newlineloc = -1
		for i in range(ret):
			if(data.startswith("\n", i)):
				newlineloc = i + 1
		endloc = data.find("\n", newlineloc)
		pfp = open(self.perms, "rb")
		pfp.seek(newlineloc + 13)
		gidata = pfp.read(4)
		pfp.close()
		return int(gidata, 16)

	def setFilePermissionUID(self, dir, val):
		pfp = open(self.perms, "rb")
		data = pfp.read()
		pfp.close()
		ret = data.find(dir)
		if(ret == -1):
			return 0
		newlineloc = -1
		for i in range(ret):
			if(data.startswith("\n", i)):
				newlineloc = i + 1
		endloc = data.find("\n", newlineloc)
		pfp = open(self.perms, "rb")
		pfp.seek(newlineloc + 8)
		uidata = pfp.write("%04X" % val)
		pfp.close()
		return int(uidata, 16)

	def setFilePermissionGID(self, dir, val):
		pfp = open(self.perms, "rb")
		data = pfp.read()
		pfp.close()
		ret = data.find(dir)
		if(ret == -1):
			return 0
		newlineloc = -1
		for i in range(ret):
			if(data.startswith("\n", i)):
				newlineloc = i + 1
		endloc = data.find("\n", newlineloc)
		pfp = open(self.perms, "rb")
		pfp.seek(newlineloc + 13)
		gidata = pfp.write("%04X" % val)
		pfp.close()
		return int(gidata, 16)

	def addPermissionEntry(self, uid, permissions, dir, groupid):
		pfp = open(self.perms, "rb")
		data = pfp.read()
		pfp.close()
		data += "%s " % permissions
		if(uid == None):
			print "UID is None!\n"
		try:
			data += hexdump(uid, "")
			data += " "
		except:
			try:
				data += "%04X " % uid
			except:
				print "UID type couldn't be confirmed..."
				return
		try:
			data += hexdump(groupid, "")
			data += " "
		except:
			try:
				data += "%04X " % groupid
			except:
				print "GID type couldn't be confirmed..."
				return
		data += "%s\n" % dir
		pfp = open(self.perms, "wb")
		pfp.write(data)
		pfp.close()
		
	def newDirectory(self, dir, perms, groupid, permtitle = 0):
		"""Creates a new directory in the NAND filesystem and adds a permissions entry."""
		if(not self.hasPermissionEntry(dir)):
			if(permtitle == 0):
				if(not os.path.isdir(self.f + dir)):
					os.mkdir(self.f + dir)
				self.addPermissionEntry(0, "d" + perms, dir, groupid)
			else:
				if(not os.path.isdir(self.f + dir)):
					os.mkdir(self.f + dir)
				self.addPermissionEntry(self.getUIDForTitleFromUIDSYS(permtitle), "d" + perms, dir, groupid)

	def newFile(self, fil, perms, groupid, permtitle = 0):
		"""Creates a new file in the NAND filesystem and adds a permissions entry."""
		if(not self.hasPermissionEntry(fil)):
			if(permtitle == 0):
				if(not os.path.isfile(self.f + fil)):
					open(self.f + fil, "wb").close()
				self.addPermissionEntry(0, "-" + perms, fil, groupid)
			else:
				if(not os.path.isfile(self.f + fil)):
					open(self.f + fil, "wb").close()
				self.addPermissionEntry(self.getUIDForTitleFromUIDSYS(permtitle), "-" + perms, fil, groupid)
	def removeFile(self, fil):
		"""Deletes a file, and removes the permissions entry."""
		os.remove(self.f + fil)
		self.removePermissionEntry(fil)

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
		ret = self.UID.getUIDForTitle(title)
		return ret

	def addTitleToMenu(self, tid):
		"""Adds a title to the System Menu."""
		a = iplsave(self.f + "/title/00000001/00000002/data/iplsave.bin", self)
		type = 0
		if(((tid & 0xFFFFFFFFFFFFFF00) == 0x0001000248414300) or ((tid & 0xFFFFFFFFFFFFFF00) == 0x0001000248414200)):
			type = 1
		a.addTitle(0,0, 0, tid, 1, type)

	def addDiscChannelToMenu(self, x, y, page, movable):
		"""Adds the disc channel to the System Menu."""
		a = iplsave(self.f + "/title/00000001/00000002/data/iplsave.bin", self)
		a.addDisc(x, y, page, movable)

	def deleteTitleFromMenu(self, tid):
		"""Deletes a title from the System Menu."""
		a = iplsave(self.f + "/title/00000001/00000002/data/iplsave.bin", self)
		a.deleteTitle(tid)

	def importTitle(self, title, add_to_menu = True, result_decrypted = False, use_version = True):
		"""When passed a prefix (the directory to obtain the .app files from, sorted by content id), a TMD instance, and a Ticket instance, this will add that title to the NAND base folder specified in the constructor. If add_to_menu is True, the title (if neccessary) will be added to the menu. The default is True. Unless is_decrypted is set, the contents are assumed to be encrypted. If result_decrypted is True, then the contents will not end up decrypted."""
		self.ES.AddTitleStart(title.tmd, None, None, True, result_decrypted, use_version = use_version)
		self.ES.AddTitleTMD(title.tmd)
		self.ES.AddTicket(title.tik)
		contents = title.tmd.getContents()
		for i, content in enumerate(contents):
			self.ES.AddContentStart(title.tmd.titleid, content.cid)
			data = title[content.index]
			self.ES.AddContentData(content.cid, data)
			self.ES.AddContentFinish(content.cid)
		self.ES.AddTitleFinish()
		if(add_to_menu == True):
			if(((tmd.tmd.titleid >> 32) != 0x00010008) and ((tmd.tmd.titleid >> 32) != 0x00000001)):
				self.addTitleToMenu(tmd.tmd.titleid)

	def getTitle(self, title_id, version = None, fakesign = True):
		title = Title()
		tmdpth = self.f + "/title/%08x/%08x/content/title.tmd" % (title >> 32, title & 0xFFFFFFFF)
		if(version != 0):
			tmdpth += ".%d" % version
		title.tmd = TMD.loadFile(tmdpth)
		if(fakesign):
			title.tmd.fakesign()
		title.tik = Ticket.loadFile(self.f + "/ticket/%08x/%08x.tik" % (title >> 32, title & 0xFFFFFFFF))
		if(fakesign):
			title.tik.fakesign()
		contents = title.tmd.getContents()
		for i in range(len(contents)):
			path = ""
			if(contents[i].type == 0x0001):
				path = self.f + "/title/%08x/%08x/content/%08x.app" % (title >> 32, title & 0xFFFFFFFF, contents[i].cid)
			elif(contents[i].type == 0x8001):
				path = self.getContentByHashFromContentMap(contents[i].hash)
			fp = open(path, "rb")
			data = fp.read()
			fp.close()
			title.contents.append(data)
		fp = open(cert, "rb")
		data = fp.read()
		fp.close()
		title.cert = data

class ISFSClass:
	"""This class contains an interface to the NAND that simulates the permissions system and all other aspects of the ISFS.
	The nand argument to the initializer is a NAND object."""
	class ISFSFP:
		def __init__(self, file, mode):
			self.fp = open(file, mode)
			self.loc = 0
			self.size = len(self.fp.read())
			self.fp.seek(0)
			self.SEEK_SET = 0
			self.SEEK_CUR = 1
			self.SEEK_END = 2
		def seek(self, where, whence = 0):
			if(whence == self.SEEK_SET):
				self.loc = where
			if(whence == self.SEEK_CUR):
				self.loc += where
			if(whence == self.SEEK_END):
				self.loc = self.size - where
			self.fp.seek(self.loc)
			return self.loc
		def close(self):
			self.fp.close()
			self.loc = 0
			self.size = 0
		def write(self, data):
			leng = self.fp.write(data)
			self.loc += leng
			return leng
		def read(self, length=""):
			if(length == ""):
				self.loc = self.size
				return self.fp.read()
			self.loc += length
			return self.fp.read(length)

	def __init__(self, nand):
		self.nand = nand
		self.f = nand.f
		self.ES = None
	def _setes(self):
		self.ES = self.nand.ES

	def _checkPerms(self, mode, uid, gid, own, grp, oth):
		if(uid == self.ES.title):
			if(own & mode):
				return 1
		elif(gid == self.ES.group):
			if(grp & mode):
				return 1
		elif(oth & mode):
			return 1
		else:
			return 0

	def Open(self, file, mode):
		if(not os.path.isfile(self.f + file)):
			return None
		modev = 0
		if(mode.find("r") != -1):
			modev = 1
		elif(mode.find("w") != -1):
			modev = 2
		if(mode.find("+") != -1):
			modev = 3
		uid = self.nand.getFilePermissionUID(file)
		gid = self.nand.getFilePermissionGID(file)
		own = self.nand.getFilePermissionOwner(file)
		grp = self.nand.getFilePermissionGroup(file)
		oth = self.nand.getFilePermissionOthers(file)
		if(self._checkPerms(modev, uid, gid, own, grp, oth) == 0):
			return -41
		return self.ISFSFP(self.f + file, mode)

	def Close(self, fp):
		fp.close()

	def Delete(self, file):
		uid = self.nand.getFilePermissionUID(file)
		gid = self.nand.getFilePermissionGID(file)
		own = self.nand.getFilePermissionOwner(file)
		grp = self.nand.getFilePermissionGroup(file)
		oth = self.nand.getFilePermissionOthers(file)
		if(self._checkPerms(2, uid, gid, own, grp, oth) == 0):
			return -41
		self.nand.removeFile(file)
		return 0

	def CreateFile(self, filename, perms):
		dirabove = filename
		uid = self.nand.getFilePermissionUID(dirabove)
		gid = self.nand.getFilePermissionGID(dirabove)
		own = self.nand.getFilePermissionOwner(dirabove)
		grp = self.nand.getFilePermissionGroup(dirabove)
		oth = self.nand.getFilePermissionOthers(dirabove)
		if(self._checkPerms(2, uid, gid, own, grp, oth) == 0):
			return -41
		self.nand.newFile(filename, perms, self.ES.group, self.ES.title)
		return 0

	def Write(self, fp, data):
		return fp.write(data)

	def Read(self, fp, length=""):
		return fp.read(length)

	def Seek(self, fp, where, whence):
		return fp.seek(where, whence)

	def CreateDir(self, dirname, perms):
		dirabove = dirname
		uid = self.nand.getFilePermissionUID(dirabove)
		gid = self.nand.getFilePermissionGID(dirabove)
		own = self.nand.getFilePermissionOwner(dirabove)
		grp = self.nand.getFilePermissionGroup(dirabove)
		oth = self.nand.getFilePermissionOthers(dirabove)
		if(self._checkPerms(2, uid, gid, own, grp, oth) == 0):
			return -41
		self.nand.newDirectory(dirname, perms, self.ES.group, self.ES.title)
		return 0

	def GetAttr(self, filename):	# Wheeee, stupid haxx to put all the numbers into one return value!
		ret = self.nand.getFilePermissionUID(filename)
		ret += (self.nand.getFilePermissionGID(filename) << 16)
		ret += (self.nand.getFilePermissionOwner(filename) << 32)
		ret += (self.nand.getFilePermissionGroup(filename) << 34)
		ret += (self.nand.getFilePermissionOthers(filename) << 36)
		return ret

	def splitAttrUID(self, attr):
		return attr & 0xFFFF
	def splitAttrGID(self, attr):
		return (attr >> 16) & 0xFFFF
	def splitAttrOwner(self, attr):
		return (attr >> 32) & 0xFF
	def splitAttrGroup(self, attr):
		return (attr >> 34) & 0xFF
	def splitAttrOthers(self, attr):
		return (attr >> 36) & 0xFF

	def Rename(self, fileold, filenew):
		uid = self.nand.getFilePermissionUID(fileold)
		gid = self.nand.getFilePermissionGID(fileold)
		own = self.nand.getFilePermissionOwner(fileold)
		grp = self.nand.getFilePermissionGroup(fileold)
		oth = self.nand.getFilePermissionOthers(fileold)
		if(self._checkPerms(2, uid, gid, own, grp, oth) == 0):
			return -41
		fld = self.nand.isFileDirectory(fileold)
		if(fld):
			print "Directory moving is busted ATM. Will fix laterz.\n"
			return -40
		fp = self.Open(fileold, "rb")
		data = fp.Read()
		fp.close()
		perms = ""
		if(own & 1):
			perms += "r"
		else:
			perms += "-"
		if(own & 2):
			perms += "w"
		else:
			perms += "-"
		if(grp & 1):
			perms += "r"
		else:
			perms += "-"
		if(grp & 2):
			perms += "w"
		else:
			perms += "-"
		if(oth & 1):
			perms += "r"
		else:
			perms += "-"
		if(oth & 2):
			perms += "w"
		else:
			perms += "-"
		self.CreateFile(filenew, perms)
		fp = self.Open(filenew, "wb")
		fp.write(data)
		fp.close()
		self.Delete(fileold)
		return 0
		
	def SetAttr(self, filename, uid, gid=0, owner=0, group=0, others=0):
		uidx = self.nand.getFilePermissionUID(filename)
		gidx = self.nand.getFilePermissionGID(filename)
		own = self.nand.getFilePermissionOwner(filename)
		grp = self.nand.getFilePermissionGroup(filename)
		oth = self.nand.getFilePermissionOthers(filename)
		if(self._checkPerms(2, uidx, gidx, own, grp, oth) == 0):
			return -41
		self.nand.setFilePermissionUID(filename, uid)
		self.nand.setFilePermissionGID(filename, gid)
		self.nand.setFilePermissionOwner(filename, owner)
		self.nand.setFilePermissionGroup(filename, group)
		self.nand.setFilePermissionOthers(filename, others)
		return 0

class ESClass:
	"""This class performs all services relating to titles installed on the Wii. It is a clone of the libogc ES interface.
	The nand argument to the initializer is a NAND object."""
	def __init__(self, nand):
		self.title = 0x0000000100000002
		self.group = 0x0001
		self.ticketadded = 0
		self.tmdadded = 0
		self.workingcid = 0
		self.workingcidcnt = 0
		self.nand = nand
		self.f = nand.f
		self.ISFS = None
	def _setisfs(self):
		self.ISFS = self.nand.ISFS
	def getContentIndexFromCID(self, tmd, cid):
		"""Gets the content index from the content id cid referenced to in the TMD instance tmd."""
		for i in range(tmd.tmd.numcontents):
			if(cid == tmd.contents[i].cid):
				return tmd.contents[i].index
		return None
	def Identify(self, id, version=0):
		if(not os.path.isfile(self.f + "/ticket/%08x/%08x.tik" % (id >> 32, id & 0xFFFFFFFF))):
			return None
		tik = Ticket.loadFile(self.f + "/ticket/%08x/%08x.tik" % (id >> 32, id & 0xFFFFFFFF))
		titleid = tik.titleid
		path = "/title/%08x/%08x/content/title.tmd" % (titleid >> 32, titleid & 0xFFFFFFFF)
		if(version):
			path += ".%d" % version
		if(not os.path.isfile(self.f + path)):
			return None
		tmd = TMD.loadFile(self.f + path)
		self.title = titleid
		self.group = tmd.tmd.group_id
		return self.title
	def GetTitleID(self):
		return self.title
	def GetDataDir(self, titleid):
		"""When passed a titleid, it will get the Titles data directory. If there is no title associated with titleid, it will return None."""
		if(not os.path.isdir(self.f + "/title/%08x/%08x/data" % (titleid >> 32, titleid & 0xFFFFFFFF))):
			return None
		return self.f + "/title/%08x/%08x/data" % (titleid >> 32, titleid & 0xFFFFFFFF)
	def GetStoredTMD(self, titleid, version=0):
		"""Gets the TMD for the specified titleid and version"""
		path = "/title/%08x/%08x/content/title.tmd" % (titleid >> 32, titleid & 0xFFFFFFFF)
		if(version):
			path += ".%d" % version
		if(not os.path.isfile(self.f + path)):
			return None
		return TMD.loadFile(self.f + path)
	def GetTitleContentsCount(self, titleid, version=0):
		"""Gets the number of contents the title with the specified titleid and version has."""
		tmd = self.GetStoredTMD(titleid, version)
		if(tmd == None):
			return 0
		return tmd.tmd.numcontents
	def GetTitleContents(self, titleid, count, version=0):
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
		self.nand.addTitleToUIDSYS(tmd.tmd.titleid)
		self.nand.newDirectory("/title/%08x" % (tmd.tmd.titleid >> 32), "rwrwr-", 0x0000)
		self.nand.newDirectory("/title/%08x/%08x" % (tmd.tmd.titleid >> 32, tmd.tmd.titleid & 0xFFFFFFFF), "rwrwr-", 0x0000)
		self.nand.newDirectory("/title/%08x/%08x/content" % (tmd.tmd.titleid >> 32, tmd.tmd.titleid & 0xFFFFFFFF), "rwrw--", 0x0000)
		self.nand.newDirectory("/title/%08x/%08x/data" % (tmd.tmd.titleid >> 32, tmd.tmd.titleid & 0xFFFFFFFF), "rw----", tmd.tmd.group_id, tmd.tmd.titleid)
		self.nand.newDirectory("/ticket/%08x" % (tmd.tmd.titleid >> 32), "rwrw--", 0x0000)
		self.workingcids = array.array('L')
		self.wtitleid = tmd.tmd.titleid
		self.is_decrypted = is_decrypted
		self.result_decrypted = result_decrypted
		self.use_version = use_version
		return
	def AddTicket(self, tik):
		"""Adds ticket to the title being added."""
		tik.dumpFile(self.f + "/tmp/title.tik")
		self.ticketadded = 1
	def DeleteTicket(self, tikview):
		"""Deletes the ticket relating to tikview
		(UNIMPLEMENTED!)"""
		return
	def AddTitleTMD(self, tmd):
		"""Adds TMD to the title being added."""
		tmd.dumpFile(self.f + "/tmp/title.tmd")
		self.tmdadded = 1
	def AddContentStart(self, titleid, cid):
		"""Starts adding a content with content id cid to the title being added with ID titleid."""
		if((self.workingcid != 0) and (self.workingcid != None)):
			"Trying to start an already existing process"
			return -41
		if(self.tmdadded):
			a = TMD.loadFile(self.f + "/tmp/title.tmd")
		else:
			a = TMD.loadFile(self.f + "/title/%08x/%08x/content/title.tmd.%d" % (self.wtitleid >> 32, self.wtitleid & 0xFFFFFFFF, tmd.tmd.title_version))
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
			self.nand.removeFile("/tmp/title.tik")
			self.ticketadded = 0
		if(self.tmdadded):
			self.nand.removeFile("/tmp/title.tmd")
			self.tmdadded = 0
		for i in range(self.workingcidcnt):
			self.nand.removeFile("/tmp/%08x.app" % self.workingcids[i])
		self.workingcidcnt = 0
		self.workingcid = None
	def AddTitleFinish(self):
		"""Finishes the adding of a title."""
		if(self.ticketadded):
			tik = Ticket.loadFile(self.f + "/tmp/title.tik")
		else:
			tik = Ticket.loadFile(self.f + "/ticket/%08x/%08x.tik" % (self.wtitleid >> 32, self.wtitleid & 0xFFFFFFFF))
		if(self.tmdadded):
			tmd = TMD.loadFile(self.f + "/tmp/title.tmd")
		contents = tmd.getContents()
		for i in range(self.workingcidcnt):
			idx = self.getContentIndexFromCID(tmd, self.workingcids[i])
			if(idx == None):
				print "Content ID doesn't exist!"
				return -42
			fp = open(self.f + "/tmp/%08x.app" % self.workingcids[i], "rb")
			if(contents[idx].type == 0x0001):
				filestr = "/title/%08x/%08x/content/%08x.app" % (self.wtitleid >> 32, self.wtitleid & 0xFFFFFFFF, self.workingcids[i])
			elif(contents[idx].type == 0x8001):
				num = self.nand.addHashToContentMap(contents[idx].hash)
				filestr = "/shared1/%08x.app" % num
			self.nand.newFile(filestr, "rwrw--", 0x0000)
			outfp = open(self.f + filestr, "wb")
			data = fp.read()
			titlekey = tik.getTitleKey()
			if(self.is_decrypted):
				tmpdata = data
			else:
				tmpdata = Crypto().decryptContent(titlekey, contents[idx].index, data)
			if(Crypto().validateSHAHash(tmpdata, contents[idx].hash) == 0):
				"Decryption failed! SHA1 mismatch."
				return -44
			if(self.result_decrypted != True):
				if(self.is_decrypted):
					tmpdata = Crypto().encryptContent(titlekey, contents[idx].index, data)
				else:
					tmpdata = data
					
			fp.close()
			outfp.write(tmpdata)
			outfp.close()
		if(self.tmdadded and self.use_version):
			self.nand.newFile("/title/%08x/%08x/content/title.tmd.%d" % (self.wtitleid >> 32, self.wtitleid & 0xFFFFFFFF, tmd.tmd.title_version), "rwrw--", 0x0000)
			tmd.dumpFile(self.f + "/title/%08x/%08x/content/title.tmd.%d" % (self.wtitleid >> 32, self.wtitleid & 0xFFFFFFFF, tmd.tmd.title_version))
		elif(self.tmdadded):
			self.nand.newFile("/title/%08x/%08x/content/title.tmd" % (self.wtitleid >> 32, self.wtitleid & 0xFFFFFFFF), "rwrw--", 0x0000)
			tmd.dumpFile(self.f + "/title/%08x/%08x/content/title.tmd" % (self.wtitleid >> 32, self.wtitleid & 0xFFFFFFFF))
		if(self.ticketadded):
			self.nand.newFile("/ticket/%08x/%08x.tik" % (self.wtitleid >> 32, self.wtitleid & 0xFFFFFFFF), "rwrw--", 0x0000)
			tik.dumpFile(self.f + "/ticket/%08x/%08x.tik" % (self.wtitleid >> 32, self.wtitleid & 0xFFFFFFFF))
		self.AddTitleCancel()
		return 0
