#----------------------------------------------------------------------
# NUS WAD Packer 1.0.1 - a (sorta) simple GUI for NUS downloading.
# (c) 2009 Xuzz (icefire) and Xuzz Productions.
#
# Wii.py (c) Xuzz, SquidMan, megazig, TheLemonMan, Omega|, and Matt_P.
#----------------------------------------------------------------------

import os, wx, shutil, sys, threading
import Wii

def readableTitleID(lower):
  out = struct.unpack("4s", struct.pack(">I", lower))
  return out[0]
  
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

queue = []

class Downloader(wx.App):
	def OnInit(self):
		self.selected = -1
		frame = wx.Frame(None, -1, "NUS WAD Packer", (150, 150), (600, 650))#, wx.SYSTEM_MENU | wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX | wx.CLOSE_BOX)
		panel = wx.Panel(frame)
		panel.Show(True)
		
		wx.StaticText(panel, -1, "NUS WAD Packer (c) 2009 Xuzz. Powered by the Wii.py framework.", (5, 5))
		
		wx.StaticText(panel, -1, "Title ID:", (5, 35))
		self.titleid = wx.TextCtrl(panel, -1, "", (60, 30), (150, -1))
		wx.StaticText(panel, -1, "Version:", (216, 35))
		self.version = wx.TextCtrl(panel, -1, "", (270, 30), (50, -1))
		
		wx.StaticText(panel, -1, "Output:", (5, 70))
		self.out = wx.TextCtrl(panel, -1, "", (60, 65), (150, -1))
		browsebtn = wx.Button(panel, -1, "Browse", (216, 65), (105, 27))
		self.Bind(wx.EVT_BUTTON, self.browse, browsebtn)
		
		wx.StaticText(panel, -1, "Output Format:", (330, 35))
		selectbox = ['WAD', 'Enc Contents', 'Dec Contents']
		self.outputtype = wx.ComboBox(panel, -1, "", (330, 65), (125, 27), choices = selectbox, style = wx.CB_READONLY)
		self.outputtype.SetStringSelection(selectbox[0]) 

		wx.StaticBox(panel, -1, "Scripting", (460, 5), (130, 86))
		loadbtn = wx.Button(panel, -1, "Load Script", (470, 25), (110, 25))
		self.Bind(wx.EVT_BUTTON, self.load, loadbtn)
		savescriptbtn = wx.Button(panel, -1, "Save Script", (470, 55), (110, 25))
		self.Bind(wx.EVT_BUTTON, self.savescript, savescriptbtn)
		
		addbtn = wx.Button(panel, -1, "Add", (5, 100), (75, -1))
		self.Bind(wx.EVT_BUTTON, self.add, addbtn)
		savebtn = wx.Button(panel, -1, "Save", (250, 100), (75, -1))
		self.Bind(wx.EVT_BUTTON, self.save, savebtn)
		
		rmbtn = wx.Button(panel, -1, "Remove", (85, 100), (75, -1))
		self.Bind(wx.EVT_BUTTON, self.remove, rmbtn)
		
		upbtn = wx.Button(panel, -1, "Up", (440, 100), (75, -1))
		self.Bind(wx.EVT_BUTTON, self.up, upbtn)
		downbtn = wx.Button(panel, -1, "Down", (520, 100), (75, -1))
		self.Bind(wx.EVT_BUTTON, self.down, downbtn)
		
		
		self.list = wx.ListCtrl(panel, -1, (5, 140), (590, 250), wx.LC_REPORT | wx.SUNKEN_BORDER)
		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.select, self.list)
		self.list.Show(True)
		self.list.InsertColumn(0, "Title ID")
		self.list.InsertColumn(1, "Version")
		self.list.InsertColumn(2, "Output")
		self.list.InsertColumn(3, "Format")
		
		
		wx.StaticText(panel, -1, "Message Log:", (5, 400))
		self.output = wx.TextCtrl(panel, -1, "", (5, 420), (590, 170), wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_DONTWRAP)
		font = wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL)
		self.output.SetFont(font)
		self.output.AppendText("NUS WAD Packer started and ready...\n\n")
		
		
		downloadbtn = wx.Button(panel, -1, "Download", (5, 600), (120, -1))
		self.Bind(wx.EVT_BUTTON, self.go, downloadbtn)
		self.progress = wx.Gauge(panel, -1, 100, (135, 605), (460, -1))
		self.progress.SetValue(0)
		
   		frame.Show(True)
		
		return True
	def getSelected(self):
		i = self.list.GetFirstSelected()
		self.selected = i
		return i
	def select(self, evt):
		if(self.getSelected() == -1):
			return
		item = queue[self.selected]
		self.titleid.SetValue(item[0])
		self.version.SetValue(item[1])
		self.out.SetValue(item[2])
		self.outputtype.SetValue(item[3])
	def setList(self):
		self.list.DeleteAllItems()
		for i, elem in enumerate(queue):
			self.list.InsertStringItem(i, elem[0])
			self.list.SetStringItem(i, 1, elem[1])
			self.list.SetStringItem(i, 2, elem[2])
			self.list.SetStringItem(i, 3, elem[3])
	def add(self, evt):
		titleid = self.titleid.GetValue()
		if(len(titleid) != 16 and not titleid.isdigit()):
			self.dialog("Title ID must be 16 numbers long! No dashes.")
			return
		ver = self.version.GetValue()
		if(not ver.isdigit() and ver != ""):
			self.dialog("Version must be all numbers!")
			return
		out = self.out.GetValue()
		fmt = self.outputtype.GetValue()
		if(not os.path.isdir(os.path.dirname(out)) and fmt == "WAD"):
			out = os.path.expanduser("~/" + getName(int(titleid, 16)))
			if(ver != ""):
				out += "v" + str(ver)
			out += ".wad"
		elif(not os.path.isdir(os.path.dirname(out))):
			out = os.path.expanduser("~/" + getName(int(titleid, 16)))
			if(ver != ""):
				out += "v" + str(ver)
		queue.append((titleid, ver, out, fmt))
		self.setList()
		self.list.Select(len(queue) - 1)
	def dialog(self, message):
		wx.MessageBox(message, "Error")
	def save(self, evt):
		if(self.getSelected() == -1):
			return
		titleid = self.titleid.GetValue()
		if(len(titleid) != 16 and titleid.isdigit()):
			self.dialog("Title ID must be 16 numbers long! No dashes.")
			return
		ver = self.version.GetValue()
		if(ver.isdigit()):
			self.dialog("Version must be all numbers!")
			return
		out = self.out.GetValue()
		fmt = self.outputtype.GetValue()
		if(not os.path.isdir(os.path.dirname(out)) and fmt == "WAD"):
			out = os.path.expanduser("~/" + getName(int(titleid, 16)))
			if(ver != ""):
				out += "v" + str(ver)
			out += ".wad"
		elif(not os.path.isdir(os.path.dirname(out))):
			out = os.path.expanduser("~/" + getName(int(titleid, 16)))
			if(ver != ""):
				out += + "v" + str(ver)
		queue[self.selected] = (titleid, ver, out, fmt)
		self.setList()
		self.list.Select(self.selected)
	def remove(self, evt):
		if(self.getSelected() == -1):
			return
		queue.pop(self.selected)
		self.setList()
		self.list.Select(min(len(queue) - 1, self.selected))
	def browse(self, evt):
		if(self.outputtype.GetValue() == "WAD"):
			dlg = wx.FileDialog(None, "Browse For Destination...", "", "", "Wii WAD files (*.wad)|*.wad|All Files (*.*)|*.*", wx.SAVE)
			if dlg.ShowModal() == wx.ID_OK:
				self.out.SetValue(dlg.GetPath())
			dlg.Destroy()
		else:
			dlg = wx.DirDialog(None, "Browse For Destination...", "")
			if dlg.ShowModal() == wx.ID_OK:
				self.out.SetValue(dlg.GetPath())
			dlg.Destroy()
	def up(self, evt):
		global queue
		if(self.getSelected() == -1):
			return
		if(self.selected == 0):
			return
		tmp1 = queue[self.selected - 1]
		tmp2 = queue[self.selected]
		queue[self.selected - 1] = tmp2
		queue[self.selected] = tmp1
		self.setList()
		self.list.Select(self.selected - 1)
		self.getSelected()
	def down(self, evt):
		global queue
		if(self.getSelected() == -1):
			return
		if(self.selected == len(queue) - 1):
			return
		tmp1 = queue[self.selected + 1]
		tmp2 = queue[self.selected]
		queue[self.selected + 1] = tmp2
		queue[self.selected] = tmp1
		self.setList()
		self.list.Select(self.selected + 1)
		self.getSelected()
	def load(self, evt):
		dlg = wx.FileDialog(None, "Open Script...", "", "", "Wii NUS Packer/Wiiimposter scripts (*.nus)|*.nus|All Files (*.*)|*.*", wx.OPEN)
		if(dlg.ShowModal() == wx.ID_OK):
			script = dlg.GetPath()
		else:
			dlg.Destroy()
			return
		dlg.Destroy()
		stuff = open(script).read().split()
		for i, arg in enumerate(stuff):
			if(len(arg) == 16 and len(stuff) != i + 1 and stuff[i + 1].isdigit()):
				tmp = (arg, str(int(stuff[i + 1], 16)), os.path.expanduser("~/" + getName(int(arg, 16)) + "v" + str(int(stuff[i + 1], 16)) + ".wad"), "WAD")
				queue.append(tmp)
		self.setList()
		self.output.AppendText("Script loaded from %s.\n" % script)
	def savescript(self, evt):
		dlg = wx.FileDialog(None, "Save Script...", "", "", "Wii NUS Packer/Wiiimposter scripts (*.nus)|*.nus|All Files (*.*)|*.*", wx.SAVE)
		if dlg.ShowModal() == wx.ID_OK:
			script = dlg.GetPath()
		else:
			dlg.Destroy()
			return
		dlg.Destroy()
		fd = open(script, "wb")
		for i, elem in enumerate(queue):
			fd.write("%08x%08x %04x\n" % (int(elem[0][:8], 16), int(elem[0][8:], 16), int(elem[1])))
		self.output.AppendText("Script written to %s.\n" % script)
	def go(self, evt):
		self.progress.SetValue(0)
		self.progress.SetRange(len(queue) * 3)
		if(os.path.isdir("tmp")):
			shutil.rmtree("tmp")
		olddir = os.getcwd()
		for i, elem in enumerate(queue):
			os.chdir(olddir)
			try:
				titleid = int(elem[0], 16)
				if(len(elem[1]) > 0):
					ver = int(elem[1])
				else:
					ver = 0
			except:
				self.output.AppendText("Invalid title %s" % elem[0])
				if(elem[1] != ""):
					self.output.AppendText(" version %s" % elem[1])
				self.output.AppendText(", skipping...\n\n")
				continue

			outfile = elem[2]
			fmt = elem[3]
			
			self.output.AppendText("Downloading %08x-%08x (%s)" % (titleid >> 32, titleid & 0xFFFFFFF, getName(titleid),))
			if(ver != 0):
				self.output.AppendText(" version %u" % ver)
			self.output.AppendText("...")
			
			self.progress.SetValue(i * 3 + 1)
			if(fmt == "Dec Contents"):
				dlthread = download(titleid, ver, True)
			else:	
				dlthread = download(titleid, ver)
			dlthread.start()
			while(dlthread.is_alive()):
				wx.Yield()
			
			self.progress.SetValue(i * 3 + 2)
			
			if(os.path.exists("tmp/tik") == False):
				self.output.AppendText("not found!\n\n")
				continue
			self.output.AppendText("done!\n")
			if(fmt == "WAD"):
				if(os.path.isdir(os.path.dirname(outfile))):
					self.output.AppendText("Packing WAD to %s..." % outfile)
					dlthread = pack("tmp", outfile)
					dlthread.start()
					while(dlthread.is_alive()):
						wx.Yield()
			else:
				if(os.path.isdir("/".join(outfile.split("/")[:-1]))):
					if(not os.path.isdir(outfile)):
						os.mkdir(outfile)
					self.output.AppendText("Copying files to %s..." % outfile)
					for file in os.listdir("tmp"):
						shutil.copy("tmp/" + file, outfile)
						wx.Yield()
			self.output.AppendText("done!\n")
			
			self.progress.SetValue(i * 3 + 3)

			self.output.AppendText("Title Info:\n")
			self.output.AppendText(str(Wii.TMD.loadFile("tmp/tmd")))
			self.output.AppendText(str(Wii.Ticket.loadFile("tmp/tik")))
			
			self.output.AppendText("\n")
			
			os.chdir(olddir)
		os.chdir(olddir)
		self.output.AppendText("Queue Downloaded!\n\n")
		
class download(threading.Thread):
	def __init__(self, titleid, ver, decrypt = True):
		threading.Thread.__init__(self)
		self.titleid = titleid
		self.ver = ver
		self.decrypt = decrypt
	def run(self):
		try:
			if(self.ver != 0):
				Wii.NUS.download(self.titleid, self.ver).dumpDir("tmp", decrypt = self.decrypt)
			else:
				Wii.NUS.download(self.titleid).dumpDir("tmp", decrypt = self.decrypt)
		except:
			pass
	
class pack(threading.Thread):
	def __init__(self, dir, outfile):
		threading.Thread.__init__(self)
		self.outfile = outfile
		self.dir = dir
	def run(self):
		try:
			Wii.WAD.loadDir(self.dir).dumpFile(self.outfile, fakesign = False)
		except:
			pass

tb = ''
def excepthook(type, value, traceb):
	import traceback
	class dummy:
		def write(self, text):
			global tb
			tb += text
	dummyf = dummy()
	traceback.print_exception(type, value, traceb, file=dummyf)
	wx.MessageBox('NUS WAD Packer has encountered a fatal error. Please inform the author of the following traceback:\n\n%s' % tb, 'Fatal Error', wx.OK | wx.ICON_ERROR)
	clean()
	sys.exit(1)

if(__name__ == '__main__'):
	dl = Downloader(redirect = False)
	dl.MainLoop()
	if(os.path.isdir(os.getcwd() + "/tmp")):
		shutil.rmtree(os.getcwd() + "/tmp")
