import os, sys, ConfigParser, zipfile
import wx
import Wii

queue = []

logdata = ''
def log(text):
	logdata.append(text + '\n')
def debug(text):
	log("[DEBUG] " + text)
def error(text):
	log("[ERROR] " + text)
	wx.MessageBox(text, 'Error', wx.OK | wx.ICON_ERROR)

class MyMenu(wx.App):
	def OnInit(self):
		self.completed = 0
		self.selected = -1
		frame = wx.Frame(None, -1, "MyMenu 1.5", (300, 200), (400, 250))
		panel = wx.Panel(frame)
		panel.Show(True)
		
		wx.StaticText(panel, -1, "MyMenu (c) 2009 Xuzz. Powered by the Wii.py framework.", (15, 230))

		wx.StaticText(panel, -1, "Source:", (5, 10), (60, 27))
		self.src = wx.TextCtrl(panel, -1, "", (65, 5), (245, 30))
		browsebtn = wx.Button(panel, -1, "Browse", (315, 5), (80, 30))
		self.Bind(wx.EVT_BUTTON, self.browse, browsebtn)
		
		addbtn = wx.Button(panel, -1, "Add", (315, 45), (80, 30))
		self.Bind(wx.EVT_BUTTON, self.add, addbtn)	
		rmbtn = wx.Button(panel, -1, "Remove", (315, 80), (80, 30))
		self.Bind(wx.EVT_BUTTON, self.remove, rmbtn)
		
		upbtn = wx.Button(panel, -1, "Up", (315, 115), (80, 30))
		self.Bind(wx.EVT_BUTTON, self.up, upbtn)
		downbtn = wx.Button(panel, -1, "Down", (315, 150), (80, 30))
		self.Bind(wx.EVT_BUTTON, self.down, downbtn)
		
		self.list = wx.ListCtrl(panel, -1, (5, 45), (300, 140), wx.LC_REPORT | wx.SUNKEN_BORDER)
		self.list.Show(True)
		self.list.InsertColumn(0, "MyMenu Scripts", 0, 290)
		
		gobtn = wx.Button(panel, -1, "Create CSM", (5, 200), (90, 30))
		self.Bind(wx.EVT_BUTTON, self.go, gobtn)
		self.progress = wx.Gauge(panel, -1, 100, (100, 200), (295, 30))
		self.progress.SetValue(0)
		
   		frame.Show(True)
		
		log("GUI Started...")
		
		return True
	def progress(self, val):
		self.progress.SetValue(self.completed * 100 + val + 50)
	def doMyMenu(self, arc, mym):
		self.progress(0)
		try:
			debug("Opening zip file %s..." % mym)
			myZip = zipfile.ZipFile(mym, 'r')
			debug("Loading INI...")
			myScript = ConfigParser.ConfigParser()
			myScript.readfp(myZip.open("mym.ini"))
		except:
			error("Invalid MyScript, skipping...")
		debug("Loaded successfully.")
		self.progress(10)
		sections = myScript.sections()

	def go(self, evt):
		self.progress.SetRange(len(queue) * 100 + 50)
		src = self.src.GetText()
		try:
			arc = Wii.U8.load(Wii.WAD.loadFile(src)[0])
		except:
			try:
				arc = Wii.U8.loadFile(src)
			except:
				error("File selected is not a WAD or a U8 file.")
				return
		try: #basic sanity checking
			assert arc['layout'] == None
			assert arc['layout/common'] == None
		except:
			error("Invalid source selected!")
			return
		
		self.progress(0)

		for elem in queue:
			arc = self.doMyMenu(arc, elem)
			self.completed += 1
			
		dlg = wx.FileDialog(None, "Save Completed File...", "", "", "Custom System Menu Files (*.csm)|*.csm|All Files (*.*)|*.*", wx.SAVE)
		if dlg.ShowModal() == wx.ID_OK:
			dst = dlg.GetPath()
			if(dst.find('.') == -1):
				dst = dst + '.csm'
			arc.dumpFile(dst)
		dlg.Destroy()
	def add(self, evt):
		dlg = wx.FileDialog(None, "Browse for Source...", "", "", "MyMenu Scripts (*.mym)|*.mym|All Files (*.*)|*.*", wx.OPEN)
		if dlg.ShowModal() == wx.ID_OK:
			queue.append(dlg.GetPath())
			log("Added " + dlg.GetPath() + " to queue.")
			self.setList()
			self.list.Select(len(queue) - 1)
		dlg.Destroy()
	def getSelected(self):
		i = self.list.GetFirstSelected()
		self.selected = i
		return i
	def setList(self):
		self.list.DeleteAllItems()
		for elem in queue:
			self.list.InsertStringItem(0, elem)
	def remove(self, evt):
		if(self.getSelected() == -1):
			return
		log("Removing " + queue[self.selected] + " from queue.")
		queue.pop(self.selected)
		self.setList()
		self.list.Select(min(len(queue) - 1, self.selected))
	def browse(self, evt):
		dlg = wx.FileDialog(None, "Browse for Source...", "", "", "Theme Bases (*.csm)|*.csm|Theme Bases (*.app)|*.app|Wii WAD files (*.wad)|*.wad|All Files (*.*)|*.*", wx.OPEN)
		if dlg.ShowModal() == wx.ID_OK:
			self.src.SetValue(dlg.GetPath())
			log("Source selected: " + dlg.GetPath())
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

mymenu = MyMenu()
mymenu.MainLoop()

"""
		cont = {}
		numcont = 0
		numelse = 0
		for sec in sections:
			if(sec[:4] == 'cont'):
				numcont += 1
		for sec in sections:
			if(sec[:4] == 'sdta' or sec[:4] == 'simg' or sec[:4] == 'cdta' or sec[:4] == 'cimg'):
				numelse += 1
		thiscont = 0
		for i, sec in enumerate(sections):
			if(sec[:4] == 'cont'):
				self.progress(10 + (20 / (numcont / thiscont))
				thiscont += 1
				
		
		self.progress(30)
		for i, sec in enumerate(sections):
			if(sec[:4] == 'sdta'):
				
			elif(sec[:4] == 'simg'):
				
			elif(sec[:4] == 'cdta'):
				
			elif(sec[:4] == 'cimg'):
"""
