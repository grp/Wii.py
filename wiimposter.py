import Wii as wii
import urllib2, struct, time, shutil, os, sys

class NUSID():
	def __init__(self, titleid, version, size):
		self.titleid = titleid
		self.version = version
		self.size = size
	def __str__(self):
		return "[soap] INFO: %08x-%08x %04x    %u\n" % (self.titleid >> 32, self.titleid & 0xFFFFFFFF, self.version, self.size)
	def rawstr(self):
		return "%08x%08x %04x %u\n" % (self.titleid >> 32, self.titleid & 0xFFFFFFFF, self.version, self.size)

def getSOAP(region): # hardcoded device id for now
	soaprequest = '<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><soapenv:Body><GetSystemUpdateRequest xmlns="urn:nus.wsapi.broadon.com"><Version>1.0</Version><MessageId>13198105123219138</MessageId><DeviceId>4362227770</DeviceId><RegionId>' + region + '</RegionId><CountryCode>' + region[:2] + '</CountryCode><TitleVersion><TitleId>0000000100000001</TitleId><Version>2</Version></TitleVersion><TitleVersion><TitleId>0000000100000002</TitleId><Version>33</Version></TitleVersion><TitleVersion><TitleId>0000000100000009</TitleId><Version>516</Version></TitleVersion><Attribute>2</Attribute><AuditData></AuditData></GetSystemUpdateRequest></soapenv:Body></soapenv:Envelope>'
	headers = {"Content-type":"text/xml; charset=utf-8", "SOAPAction":'"urn:nus.wsapi.broadon.com/"', "User-agent":"wii libnup/1.0"}
	request = urllib2.Request("http://nus.shop.wii.com/nus/services/NetUpdateSOAP", soaprequest, headers)
	f = urllib2.urlopen(request)
	data = f.read()
	
	titles = []
	
	data = data[data.find("</UncachedContentPrefixURL>") + len("</UncachedContentPrefixURL>"):data.find("<UploadAuditData>")]
	for i in range(data.count("<TitleId>")):
		title = data[data.find("<TitleVersion>"):data.find("</TitleVersion>") + len("</TitleVersion>")]
		
		titleid = int(data[data.find("<TitleId>") + len("<TitleId>"):data.find("</TitleId>")], 16) #16 for hex
		version = int(data[data.find("<Version>") + len("<Version>"):data.find("</Version>")])
		size = int(data[data.find("<FsSize>") + len("<FsSize>"):data.find("</FsSize>")])
		
		nus = NUSID(titleid, version, size)
		titles.append(nus)
		
		data = data[data.find("</TitleVersion>") + len("</TitleVersion>"):]
	return titles
	
def readableTitleID(lower):
	out = struct.unpack("4s", struct.pack(">I", lower))
	return out[0]
	
def log(text):
	sys.stdout.write(text)
	sys.stdout.flush()
	
def getName(titleid):
	upper = (titleid >> 32)
	lower = (titleid & 0xFFFFFFFF)
	if(upper == 0x00000001):
		if(lower > 0x02 and lower < 0x100):
			return "IOS%d" % lower
		elif(lower == 0x02):
			return "SystemMenu"
		elif(lower == 0x100):
			return "BC"
		elif(lower == 0x101):
			return "MIOS"
		else:
			return "Unknown System Title (%08x)" % lower
	elif(upper == 0x00010002 or upper == 0x00010008):
		read = readableTitleID(lower)
		
		if(read[3] == "K"):
			rgn = "Korea"
		elif(read[3] == "A"):
			rgn = "All Regions"
		elif(read[3] == "P"):
			rgn = "Europe/PAL"
		elif(read[3] == "E"):
			rgn = "North America"
		elif(read[3] == "J"):
			rgn = "Japan"
		else:
			rgn = "Unknown Region"
				
		if(read[:3] == "HAB"):
			return "Wii Shop Channel (%s)" % rgn
		if(read[:3] == "HAL"):
			return "EULA (%s)" % rgn
		if(read[:3] == "HAA"):
			return "Photo Channel (%s)" % rgn
		if(read[:3] == "HAC"):
			return "Mii Channel (%s)" % rgn
		if(read[:3] == "HAE"):
			return "Wii Message Board (%s)" % rgn
		if(read[:3] == "HAF"):
			return "Weather Channel (%s)" % rgn
		if(read[:3] == "HAG"):
			return "News Channel (%s)" % rgn
		if(read[:3] == "HAK"):
			return "Region Select (%s)" % rgn
		if(read[:3] == "HAY"):
			return "Photo Channel 1.1 (%s)" % rgn
		
			
		if(upper == 0x00010002):
			return "Channel '%s'" % read
		if(upper == 0x00010008):
			return "Hidden Channel '%s'" % read
	else:
		return "Other (%08x-%08x)" % (upper, lower)
	
def summary(report, item):
	tmd = wii.TMD.loadFile("%08x%08x/tmd" % (item.titleid >> 32, item.titleid & 0xFFFFFFFF)) #not tmp/ because we are already in tmp
	report.write(getName(item.titleid) + "\n")
	report.write(" Title ID: %08x-%08x\n" % (item.titleid >> 32, item.titleid & 0xFFFFFFFF))
	report.write(" Version: 0x%04x\n Size: %u\n" % (item.version, item.size))
	shared = 0
	contents = tmd.getContents()
	for i in range(len(contents)):
		if(contents[i].type & 0x8000):
			shared += 1
	report.write(" Contents: %u (of which %u are shared)\n\n" % (len(contents), shared))
	

def detailed(report, item):
	tmd = wii.TMD.loadFile("tmp/%08x%08x/tmd" % (item.titleid >> 32, item.titleid & 0xFFFFFFFF))
	tik = wii.Ticket.loadFile("tmp/%08x%08x/tik" % (item.titleid >> 32, item.titleid & 0xFFFFFFFF))
	
	log("Importing %s to fake NAND (decrypted)..." % getName(item.titleid))
	wii.NAND("nand").importTitle("tmp/%08x%08x" % (item.titleid >> 32, item.titleid & 0xFFFFFFFF), tmd, tik, is_decrypted = False, result_decrypted = True)
	log("Done!\n")
	
	log("Importing %s to fake NAND (encrypted)..." % getName(item.titleid))
	wii.NAND("encnand").importTitle("tmp/%08x%08x" % (item.titleid >> 32, item.titleid & 0xFFFFFFFF), tmd, tik, is_decrypted = False, result_decrypted = False)
	log("Done!\n")
	
	shutil.copy("tmp/%08x%08x/cert" % (item.titleid >> 32, item.titleid & 0xFFFFFFFF), "nand/sys/cert.sys")
	shutil.copy("tmp/%08x%08x/cert" % (item.titleid >> 32, item.titleid & 0xFFFFFFFF), "encnand/sys/cert.sys")

	report.write(getName(item.titleid) + "\n")
	report.write(" Title ID: %08x-%08x\n" % (item.titleid >> 32, item.titleid & 0xFFFFFFFF))
	report.write(" Version: 0x%04x\n  Size: %u\n" % (item.version, item.size))
	
	report.write(str(tmd))
		
	#do TMD signature and certs. TODO!
	
	report.write(str(tik))
	
	#do Ticket signature and certs. TODO!
	
	report.write("\n\n")

class nullFile:
	def _null(self, *args, **kwds):
		pass
	def __getattr__(self, name):
		return self._null

	
def changed(region, added, removed, modified, previous, no_log = False):
	if(no_log):
		report = nullFile()
	else:
		report = open("reports/%s/%s.log" % (region, time.strftime("%y%m%d-%I%M%S")), "wb")
	report.write("************************************************************************\n*********************** Wii System Update Report ***********************\n************************************************************************\n\n")
	report.write("Titles added:\t%u\n" % len(added))
	report.write("Titles changed:\t%u\n" % len(modified))
	report.write("Titles removed:\t%u\n" % len(removed))
	
	report.write("\n************************** SUMMARY OF CHANGES **************************\n")
	
	os.chdir("tmp")
	
	if(len(added) > 0):
		report.write("\n====== Titles Added ======\n\n")
	for item in added:
		log("Downloading %s..." % getName(item.titleid))
		wii.NUS(item.titleid, item.version).download(useidx = False, decrypt = False)
		log("Done!\n")
		summary(report, item)
		
	if(len(modified) > 0):
		report.write("\n====== Titles Changed ======\n\n")
	for item in modified:
		log("Downloading %s..." % getName(item.titleid))
		wii.NUS(item.titleid, item.version).download(useidx = False, decrypt = False)
		log("Done!\n")
		summary(report, item)
		
	if(len(removed) > 0):
		report.write("\n====== Titles Removed (showing info from last available version) ======\n\n")
	for item in removed:
		summary(report, item)
		
	os.chdir("..")
		
	report.write("\n**************************** DETAILED DUMPS ****************************\n")
	
	if(len(added) > 0):
		report.write("\n====== Titles Added ======\n\n")
	for item in added:
		detailed(report, item)
		shutil.rmtree("tmp/%08x%08x" % (item.titleid >> 32, item.titleid & 0xFFFFFFFF))
		
	if(len(modified) > 0):
		report.write("\n====== Titles Changed ======\n\n")
	for item in modified:
		detailed(report, item)
		shutil.rmtree("tmp/%08x%08x" % (item.titleid >> 32, item.titleid & 0xFFFFFFFF))
		
	if(len(removed) > 0):
		report.write("\n====== Titles Removed (showing info from last available version) ======\n\n")
	for item in removed:
		detailed(report, item)
		
	report.write("\n***************************** MESSAGE LOG *****************************\n")
	if(no_log != True):
		report.write(open("runlog.%s.txt" % region).read())


def imposter(regions):
	for region in regions:
		log("Wiimpostor invoked for region %s...\n" % region)
	
		data = ""
		data += "[check] INFO: Wiimposter: Check invoked for region %s\n" % region
		try:
			nodb = False
			last = open("lastupdate.%s.txt" % region, "rb").read()
		except:
			data += "[titlelist] WARNING: TitleList: DB file lastupdate.%s.txt does not exist. Initializing to blank list.\n" % region
			nodb = True
		
		data += "[soap] INFO: Checking for updates...\n"
	
		data += ("[soap] INFO: Title ID          Version FsSize\n")
	
		log("Getting list of titles from Nintendo's SOAP server...")
		soap = getSOAP(region)
		for entry in soap:
			data += str(entry)
		log("Done!\n")
			
		if(nodb):
			old = []
		else:
			old = last.split("\n")
			topop = []
			for i in range(len(old)):
				elem = old[i]
				if(elem == ""):
					topop.append(i) # >_>
					continue
				elem = elem.split(" ")
				titleid = int(elem[0], 16)
				version = int(elem[1], 16)
				sz = int(elem[2])
				tmp = NUSID(titleid, version, sz) #is a tmp var needed?
				old[i] = tmp
		
			popped = 0 #don't ask me why I did this
			for pop in topop:
				old.pop(pop - popped)
				popped += 1
		
		#the code from here on down makes no sesne to me already. Dont ask.
		
		added  = []
		removed = []
		modified = []
		same = []
		previous = []
		
		log("Checking for titles removed, modified, or added...")
		for elem in old:
			cookie_jar = len(soap)
			for title in soap:
				if(elem.titleid != title.titleid):
					cookie_jar -= 1
				elif(elem.version != title.version): #don't check sizes because nintendo randomly changes them
					modified.append(title)
					previous.append(elem)
				else:
					same.append(title)
			if(cookie_jar == 0):
				removed.append(elem)
				
		for title in soap:
			cookie_jar = len(old)
			for elem in old:
				if(elem.titleid != title.titleid):
					cookie_jar -= 1
			if(cookie_jar == 0):
				added.append(title)
		log("Done!\n")
				
		#end code I don't get anymore
		
		if(not os.path.isdir("reports")):
			os.mkdir("reports")
		if(not os.path.isdir("reports/USA")):
			os.mkdir("reports/USA")
		if(not os.path.isdir("reports/EUR")):
			os.mkdir("reports/EUR")
		if(not os.path.isdir("reports/JPN")):
			os.mkdir("reports/JPN")
		if(not os.path.isdir("reports/KOR")):
			os.mkdir("reports/KOR")
		if(not os.path.isdir("tmp")):
			os.mkdir("tmp")
				
		data += "[soap] INFO: Comparing update with previous...\n"
		data += "[soap] INFO: %u added, %u removed, %u changed, %u unchanged" % (len(added), len(removed), len(modified), len(same))
				
		open("runlog.%s.txt" % region, "wb").write(data)
		
		if(len(added) != 0 or len(modified) != 0 or len(removed) != 0):
			updatelog = ""
			for title in soap:
				updatelog += title.rawstr()
			open("lastupdate.%s.txt" % region, "wb").write(updatelog)
			changed(region, added, removed, modified, previous)
		else:
			log("No new update for this region!\n")
		log("Complete for region %s!\n\n" % region)
			

if(__name__ == "__main__"):
	available = ["USA", "EUR", "JPN", "KOR"]
	script = 0
	if(len(sys.argv) > 1):
		script = 1
		if(os.path.isfile(sys.argv[1])):
			stuff = open(sys.argv[1]).read().split()
		else:
			stuff = sys.argv[1:]
		for i, arg in enumerate(stuff):
			if(arg in available):
				imposter(args)
			elif(len(arg) == 16 and len(stuff) != i + 1 and stuff[i + 1].isdigit()):
				tmp = NUSID(int(arg, 16), int(stuff[i + 1]), 0)
				changed("", [tmp], [], [], [], no_log = True)

	if(script == 0):
		imposter(available)
	
	
