import os, struct, subprocess, fnmatch, shutil, urllib, array
from PIL import Image

from Struct import Struct

from common import *

def flatten(myTuple):
	if (len(myTuple) == 4):
		return myTuple[0] << 0 | myTuple[1] << 8 | myTuple[2] << 16 | myTuple[3] << 24
	else:
		return myTuple[0] << 0 | myTuple[1] << 8 | myTuple[2] << 16 | 0xff << 24

def round_up(x, n):
	left = x % n
	return x + left

def avg(w0, w1, c0, c1):
	a0 = c0 >> 11
	a1 = c1 >> 11
	a = (w0*a0 + w1*a1) / (w0 + w1)
	c = (a << 11) & 0xffff

	a0 = (c0 >> 5) & 63
	a1 = (c1 >> 5) & 63
	a = (w0*a0 + w1*a1) / (w0 + w1)
	c = c | ((a << 5) & 0xffff)

	a0 = c0 & 31
	a1 = c1 & 31
	a = (w0*a0 + w1*a1) / (w0 + w1)
	c = c | a

	return c


class TPL():
	"""This is the class to generate TPL texutres from PNG images, and to convert TPL textures to PNG images. The parameter file specifies the filename of the source, either a PNG image or a TPL image.
	
	Currently supported are the following formats to convert from TPL: RGBA8, RGB565, I4, IA4, I8, IA8, CI4, CI8, CMP, CI14X2. Currently not working is RBG5A3. RBG5A3 is having alpha issues, i'm working on it.
	
	Currently support to convert to TPL: I4, I8, IA4, IA8, RBG565, RBGA8. Currently not working/done are CI4, CI8, CMP, CI14X2, and RBG5A3. RBG5A3 is having alpha issues."""
	
	
	class TPLHeader(Struct):
		__endian__ = Struct.BE
		def __format__(self):
			self.magic = Struct.uint32
			self.ntextures = Struct.uint32
			self.header_size = Struct.uint32
	class TPLTexture(Struct):
		__endian__ = Struct.BE
		def __format__(self):
			self.header_offset = Struct.uint32
			self.palette_offset = Struct.uint32
	class TPLTextureHeader(Struct):
		__endian__ = Struct.BE
		def __format__(self):
			self.height = Struct.uint16
			self.width = Struct.uint16
			self.format = Struct.uint32
			self.data_off = Struct.uint32
			self.wrap = Struct.uint32[2]
			self.filter = Struct.uint32[2]
			self.lod_bias = Struct.float
			self.edge_lod = Struct.uint8
			self.min_lod = Struct.uint8
			self.max_lod = Struct.uint8
			self.unpacked = Struct.uint8
	class TPLPaletteHeader(Struct):
		__endian__ = Struct.BE
		def __format__(self):
			self.nitems = Struct.uint16
			self.unpacked = Struct.uint8
			self.pad = Struct.uint8
			self.format = Struct.uint32
			self.offset = Struct.uint32
	def __init__(self, file):
		if(os.path.isfile(file)):
			self.file = file
			self.data = None
		else:
			self.file = None
			self.data = file
	def toTPL(self, outfile, (width, height) = (None, None), format = "RGBA8"): #single texture only
		"""This converts an image into a TPL. The image is specified as the file parameter to the class initializer, while the output filename is specified here as the parameter outfile. Width and height are optional parameters and specify the size to resize the image to, if needed. Returns the output filename.
		
		This only can create TPL images with a single texture."""
		head = self.TPLHeader()
		head.magic = 0x0020AF30
		head.ntextures = 1
		head.header_size = 0x0C
		
		tex = self.TPLTexture()
		tex.header_offset = 0x14
		tex.pallete_offset = 0
		
		img = Image.open(self.file)
		theWidth, theHeight = img.size
		if(width != None and height != None and (width != theWidth or height != theHeight)):
			img = img.resize((width, height), Image.ANTIALIAS)
		w, h = img.size
		
		texhead = self.TPLTextureHeader()
		texhead.height = h
		texhead.width = w
		if format == "I4":
			texhead.format = 0
			tpldata = self.toI4((w, h), img)
		elif format == "I8":
			texhead.format = 1
			tpldata = self.toI8((w, h), img)
		elif format == "IA4":
			texhead.format = 2
			tpldata = self.toIA4((w, h), img)
		elif format == "IA8":
			texhead.format = 3
			tpldata = self.toIA8((w, h), img)
		elif format == "RGB565":
			texhead.format = 4
			tpldata = self.toRGB565((w, h), img)
		elif format == "RGB5A3":
			texhead.format = 5
			tpldata = self.toRGB5A3((w, h), img)
		elif format == "RGBA8":
			texhead.format = 6
			tpldata = self.toRGBA8((w, h), img)
		elif format == "CI4":
			texhead.format = 8
			''' ADD toCI4 '''
			raise Exception("toCI4 not done")
			#tpldata = self.toCI4((w, h), img)
		elif format == "CI8":
			texhead.format = 9
			''' ADD toCI8 '''
			raise Exception("toCI8 not done")
			#tpldata = self.toCI8((w, h), img)
		elif format == "CI14X2":
			texhead.format = 10
			''' ADD toCI14X2 '''
			raise Exception("toCI14X2 not done")
			#tpldata = self.toCI14X2((w, h), img)
		elif format == "CMP":
			texhead.format = 14
			''' ADD toCMP '''
			raise Exception("toCMP not done")
			#tpldata = self.toCMP((w, h), img)
			
		texhead.data_off = 0x14 + len(texhead)
		texhead.wrap = [0, 0]
		texhead.filter = [1, 1]
		texhead.lod_bias = 0
		texhead.edge_lod = 0
		texhead.min_lod = 0
		texhead.max_lod = 0
		texhead.unpacked = 0
		
		f = open(outfile, "wb")
		f.write(head.pack())
		f.write(tex.pack())
		f.write(texhead.pack())
		if format == "I4":
			f.write(struct.pack(">" + str(align(w,4) * align(h,4) / 2) + "B", *tpldata))
		if format == "I8":
			f.write(struct.pack(">" + str(align(w,4) * align(h,4) * 1) + "B", *tpldata))
		if format == "IA4":
			f.write(struct.pack(">" + str(align(w,4) * align(h,4) * 1) + "B", *tpldata))
		if format == "IA8":
			f.write(struct.pack(">" + str(align(w,4) * align(h,4) * 1) + "H", *tpldata))
		if format == "RGB565":
			f.write(struct.pack(">" + str(align(w,4) * align(h,4) * 1) + "H", *tpldata))
		if format == "RGB5A3":
			f.write(struct.pack(">" + str(align(w,4) * align(h,4) * 1) + "H", *tpldata))
		if format == "RGBA8":
			f.write(struct.pack(">" + str(align(w,4) * align(h,4) * 4) + "B", *tpldata))
		if format == "CI4":
			''' ADD toCI4 '''
			#f.write(struct.pack(">"+ str(align(w,4) * align(h,4) * 4) + "B", *tpldata))
		if format == "CI8":
			''' ADD toCI8 '''
			#f.write(struct.pack(">"+ str(align(w,4) * align(h,4) * 4) + "B", *tpldata))
		if format == "CI14X2":
			''' ADD toCI14X2 '''
			#f.write(struct.pack(">"+ str(align(w,4) * align(h,4) * 4) + "B", *tpldata))
		if format == "CMP":
			''' ADD toCMP '''
			#f.write(struct.pack(">"+ str(align(w,4) * align(h,4) * 4) + "B", *tpldata))
		f.close()
		
		return outfile
	def toI4(self, (w, h), img):
		out = [0 for i in range(align(w, 4) * align(h, 4) / 2)]
		outp = 0
		inp = list(img.getdata())
		for y1 in range(0, h, 8):
			for x1 in range(0, w, 8):
				for y in range(y1, y1+8, 1):
					for x in range(x1, x1+8, 2):
						if x>=w or y>=h:
							newpixel = 0
						else:
							rgba = flatten(inp[x+y*w])
							r = (rgba >> 0) & 0xff
							g = (rgba >> 8) & 0xff
							b = (rgba >> 16) & 0xff
							i1 = ((r + g + b) / 3) & 0xff
							rgba = flatten(inp[x+1+y*w])
							r = (rgba >> 0) & 0xff
							g = (rgba >> 8) & 0xff
							b = (rgba >> 16) & 0xff
							i2 = ((r + g + b) / 3) & 0xff

							newpixel = (((i1 * 15) / 255) << 4)
							newpixel |= (((i2 * 15) / 255) & 0xf)
						out[outp] = newpixel
						outp += 1
		return out
	def toI8(self, (w, h), img):
		out = [0 for i in range(align(w, 4) * align(h, 4))]
		outp = 0
		inp = list(img.getdata())
		for y1 in range(0, h, 4):
			for x1 in range(0, w, 8):
				for y in range(y1, y1+4, 1):
					for x in range(x1, x1+8, 1):
						rgba = flatten(inp[x + (y * w)])
						if x>= w or y>=h:
							i1 = 0
						else:
							r = (rgba >> 0) & 0xff
							g = (rgba >> 8) & 0xff
							b = (rgba >> 16) & 0xff
							i1 = ((r + g + b) / 3) & 0xff
						out[outp] = i1
						outp += 1
		return out
	def toIA4(self, (w, h), img):
		out = [0 for i in range(align(w, 4) * align(h, 4))]
		outp = 0
		inp = list(img.getdata())
		for y1  in range(0, h, 4):
			for x1 in range(0, w, 8):
				for y in range(y1, y1+4, 1):
					for x in range(x1, x1+8, 1):
						if x>=w or y>=h:
							newpixel = 0
						else:
							rgba = flatten(inp[x + (y * w)])
							r = (rgba >> 0) & 0xff
							g = (rgba >> 8) & 0xff
							b = (rgba >> 16) & 0xff
							i1 = ((r + g + b) / 3) & 0xff
							a1 = (rgba >> 24) & 0xff

							newpixel = (((i1 * 15) / 255) & 0xf)
							newpixel = newpixel | (((a1 * 15) / 255) << 4)
						out[outp] = newpixel
						outp += 1
		return out
	def toIA8(self, (w, h), img):
		out = [0 for i in range(align(w, 4) * align(h, 4))]
		outp = 0
		inp = list(img.getdata())
		for y1 in range(0, h, 4):
			for x1 in range(0, w, 4):
				for y in range(y1, y1+4, 1):
					for x in range(x1, x1+4, 1):
						if x>=w or y>=h:
							newpixel = 0
						else:
							rgba = flatten(inp[x + (y * w)])
							r = (rgba >> 0) & 0xff
							g = (rgba >> 8) & 0xff
							b = (rgba >> 16) & 0xff
							i1 = ((r + g + b) / 3) & 0xff
							a1 = (rgba >> 24) & 0xff

							newpixel = i1 << 8
							newpixel = newpixel | a1
						out[outp] = newpixel
						outp += 1
		return out
	def toRGB565(self, (w, h), img):
		out = [0 for i in range(align(w, 4) * align(h, 4))]
		outp = 0
		inp = img.getdata()
		for y1 in range(0, h, 4):
			for x1 in range(0, w, 4):
				for y in range(y1, y1+4, 1):
					for x in range(x1, x1+4, 1):
						newpixel = 0
						if x>=w or y>=h:
							newpixel = 0
						else:
							rgba = flatten(inp[x+y*w])
							r = (rgba >> 0) & 0xff
							g = (rgba >> 8) & 0xff
							b = (rgba >> 16) & 0xff
							newpixel = ((b >>3) << 11) | ((g >>2) << 5) | ((r >>3) << 0)
						out[outp] = newpixel
						outp += 1
		return out
	def toRGB5A3(self, (w, h), img):
		out = [0 for i in range(align(w, 4) * align(h, 4))]
		outp = 0
		inp = list(img.getdata())
		for y1 in range(0, h, 4):
			for x1 in range(0, w, 4):
				for y in range(y1, y1+4, 1):
					for x in range(x1, x1+4, 1):
						newpixel = 0
						if x>=w or y>=h:
							newpixel = 0
						else:
							rgba = flatten(inp[x + (y * h)])
							r = (rgba >> 0) &  0xff
							g = (rgba >> 8) &  0xff
							b = (rgba >> 16) & 0xff
							a = (rgba >> 24) & 0xff
							if (a <= 0xda):
								newpixel &= ~(1 << 15)
								r = ((r * 15)  / 255) & 0xf
								g = ((g * 15)  / 255) & 0xf
								b = ((b * 15)  / 255) & 0xf
								a = ((a * 7)   / 255) & 0x7
								#newpixel |= r << 12
								#newpixel |= g << 8
								#newpixel |= b << 4
								#newpixel |= a << 0
								newpixel |= a << 12
								newpixel |= b << 8
								newpixel |= g << 4
								newpixel |= r << 0
							else:
								newpixel |= (1 << 15)
								r = ((r * 31) / 255) & 0x1f
								g = ((g * 31) / 255) & 0x1f
								b = ((b * 31) / 255) & 0x1f
								newpixel |= b << 10
								newpixel |= g << 5
								newpixel |= r << 0
						out[outp] = newpixel
						outp += 1
		return out
	def toRGBA8(self, (w, h), img):
		out = [0 for i in range(align(w, 4) * align(h, 4) * 4)]
		inp = list(img.getdata())
		iv = 0
		z = 0
		lr = [0 for i in range(32)]
		lg = [0 for i in range(32)]
		lb = [0 for i in range(32)]
		la = [0 for i in range(32)]
		for y1 in range(0, h, 4):
			for x1 in range(0, w, 4):
				for y in range(y1, y1 + 4, 1):
					for x in range(x1, x1 + 4, 1):
						if(y >= h or x >= w):
							lr[z] = 0
							lg[z] = 0
							lb[z] = 0
							la[z] = 0
						else:
							rgba = flatten(inp[x + (y * w)])
						lr[z] = (rgba >> 0) & 0xff
						lg[z] = (rgba >> 8) & 0xff
						lb[z] = (rgba >> 16) & 0xff
						la[z] = (rgba >> 24) & 0xff
						z += 1
				if(z == 16):
					for i in range(16):
						out[iv] = la[i] & 0xff
						iv += 1
						out[iv] = lr[i] & 0xff
						iv += 1
					for i in range(16):
						out[iv] = lg[i] & 0xff
						iv += 1
						out[iv] = lb[i] & 0xff
						iv += 1
					z = 0
		return out
	def toImage(self, outfile):
		"""This converts a TPL texture to a PNG image. You specify the input TPL filename in the initializer, and you specify the output filename in the outfile parameter to this method. Returns the output filename.
		
		This only supports single textured TPL images."""
		if(self.file):
			data = open(self.file, "rb").read()
		else:
			data = self.data
		
		header = self.TPLHeader()
		textures = []
		pos = 0
		
		header.unpack(data[pos:pos + len(header)])
		pos += len(header)
		
		palette_offsets = []
		
		for i in range(header.ntextures):
			tmp = self.TPLTexture()
			tmp.unpack(data[pos:pos + len(tmp)])
			textures.append(tmp)
			pos += len(tmp)
			if(tmp.palette_offset > 0):
				palette_offsets.append(tmp.palette_offset)
		
		if(header.ntextures > 1):
			raise ValueError("Only one texture supported. Don't touch me!")
		
		for i in range(header.ntextures):
			head = textures[i]
			tex = self.TPLTextureHeader()
			tex.unpack(data[head.header_offset:head.header_offset + len(tex)])
			w = tex.width
			h = tex.height
		
			if(tex.format == 0): #I4, 4-bit
				tpldata = struct.unpack(">" + str((w * h) / 2) + "B", data[tex.data_off:tex.data_off + ((w * h) / 2)])
				rgbdata = self.I4((w, h), tpldata)
			
			elif(tex.format == 1): #I8, 8-bit
				tpldata = struct.unpack(">" + str(w * h) + "B", data[tex.data_off:tex.data_off + (w * h * 1)])
				rgbdata = self.I8((w, h), tpldata)
			elif(tex.format == 2): #IA4, 8-bit
				tpldata = struct.unpack(">" + str(w * h) + "B", data[tex.data_off:tex.data_off + (w * h * 1)])
				rgbdata = self.IA4((w, h), tpldata)
			
			elif(tex.format == 4): #RGB565, 16-bit
				tpldata = data[tex.data_off:]
				rgbdata = self.RGB565((w, h), tpldata)
			elif(tex.format == 5): #RGB5A3, 16-bit
				tpldata = data[tex.data_off:]
				rgbdata = self.RGB5A3((w, h), tpldata)
			elif(tex.format == 3): #IA8, 16-bit
				tpldata = data[tex.data_off:]
				rgbdata = self.IA8((w, h), tpldata)
			
			elif(tex.format == 6): #RGBA8, 32-bit, but for easyness's sake lets do it with 16-bit
				tpldata = data[tex.data_off:]
				rgbdata = self.RGBA8((w, h), tpldata)
				
			elif(tex.format == 8 or tex.format == 9 or tex.format == 10):
				palhead = self.TPLPaletteHeader()
				offs = palette_offsets.pop(0)
				palhead.unpack(data[offs:offs + len(palhead)])

				tpldata = struct.unpack(">" + str(palhead.nitems) + "H", data[palhead.offset:palhead.offset + (palhead.nitems * 2)])
				if(palhead.format == 0):
					palette_data = self.IA8((palhead.nitems, 1), tpldata)[0]
				elif(palhead.format == 1):
					palette_data = self.RGB565((palhead.nitems, 1), tpldata)[0]
				elif(palhead.format == 2):
					palette_data = self.RGB5A3((palhead.nitems, 1), tpldata)[0]
				
				paldata = []
				for i in range(0, palhead.nitems * 4, 4):
					tmp = 0
					tmp |= palette_data[i + 0] << 24
					tmp |= palette_data[i + 1] << 16
					tmp |= palette_data[i + 2] << 8
					tmp |= palette_data[i + 3] << 0
					paldata.append(tmp)
				
				if(tex.format == 8):
					tpldata = struct.unpack(">" + str((w * h) / 2) + "B", data[tex.data_off:tex.data_off + ((w * h) / 2)])
					rgbdata = self.CI4((w, h), tpldata, paldata)
				if(tex.format == 9):
					tpldata = struct.unpack(">" + str(w * h) + "B", data[tex.data_off:tex.data_off + (w * h * 1)])
					rgbdata = self.CI8((w, h), tpldata, paldata)
				if(tex.format == 10):
					tpldata = struct.unpack(">" + str(w * h) + "H", data[tex.data_off:tex.data_off + (w * h * 2)])
					rgbdata = self.CI14X2((w, h), tpldata, paldata)
			elif(tex.format == 14):
				tpldata = ''.join(data[tex.data_off:])
				
				rgbdata = self.CMP((w, h), tpldata)
			else:
				raise TypeError("Unsupported TPL Format: " + str(tex.format))
		
		output = Image.fromstring("RGBA", (w, h), rgbdata)
		ext = outfile[outfile.rfind(".")+1:]
		output.save(outfile, ext)
		
		return outfile
	def getSizes(self):
		"""This returns a tuple containing the width and height of the TPL image filename in the class initializer. Will only return the size of single textured TPL images."""
		data = open(self.file, "rb").read()
		
		header = self.TPLHeader()
		textures = []
		pos = 0
		
		header.unpack(data[pos:pos + len(header)])
		pos += len(header)
		
		for i in range(header.ntextures):
			tmp = self.TPLTexture()
			tmp.unpack(data[pos:pos + len(tmp)])
			textures.append(tmp)
			pos += len(tmp)
		
		for i in range(header.ntextures):
			head = textures[i]
			tex = self.TPLTextureHeader()
			tex.unpack(data[head.header_offset:head.header_offset + len(tex)])
			w = tex.width
			h = tex.height
		return (w, h)
	def toScreen(self): #single texture only
		"""This will draw a simple window with the TPL image displayed on it. It uses WxPython for the window creation and management. The window has a minimum width and height of 300 x 200. Does not return a value.
		
		Again, only a single texture is supported."""
		import wx
		class imp(wx.Panel):
			def __init__(self, parent, id, im):
				wx.Panel.__init__(self, parent, id)
				w = img.GetWidth()
				h = img.GetHeight()
				wx.StaticBitmap(self, -1, im, ( ((max(w, 300) - w) / 2), ((max(h, 200) - h) / 2) ), (w, h))

		self.toImage("tmp.png")
		img = wx.Image("tmp.png", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
		w = img.GetWidth()
		h = img.GetHeight()
		app = wx.App(redirect = False)
		frame = wx.Frame(None, -1, "TPL (" + str(w) + ", " + str(h) + ")", size = (max(w, 300), max(h, 200)))
		image = imp(frame, -1, img)
		frame.Show(True)
		app.MainLoop()
		os.unlink("tmp.png")
	def RGBA8(self, (x, y), data):
		out = [0 for i in range(x * y)]
		inp = 0
		for i in xrange(0, y, 4):
			for j in xrange(0, x, 4):
				for k in xrange(2):
					for l in xrange(i, i + 4, 1):
						for m in xrange(j, j + 4, 1):
							texel = Struct.uint16(data[inp * 2:inp * 2 + 2], endian = '>')
							inp += 1
							if (m >= x) or (l >= y):
								continue
							if k == 0:
								a = (texel >> 8) & 0xff
								r = (texel >> 0) & 0xff
								out[m + (l * x)] = out[m + (l * x)] | ((r<<0) | (a<<24))
							else:
								g = (texel >> 8) & 0xff
								b = (texel >> 0) & 0xff
								out[m + (l * x)] = out[m + (l * x)] | ((g<<8) | (b<<16))
		return ''.join(Struct.uint32(p) for p in out)
	def RGB5A3(self, (w, h), jar):
		out = [0 for i in range(w * h)]
		i = 0
		for y in range(0, h, 4):
			for x in range(0, w, 4):
				for y1 in range(y, y + 4):
					for x1 in range(x, x + 4):
						if(y1 >= h or x1 >= w):
							continue
						pixel = Struct.uint16(jar[i * 2:i * 2 + 2], endian='>')
						i += 1
						
						if(pixel & (1 << 15)): #RGB555
							b = (((pixel >> 10) & 0x1F) * 255) / 31
							g = (((pixel >> 5) & 0x1F) * 255) / 31
							r = (((pixel >> 0) & 0x1F) * 255) / 31
							a = 255
						else: #RGB4A3
							a = (((pixel >> 12) & 0x07) * 255) / 7
							b = (((pixel >> 8) & 0x0F) * 255) / 15
							g = (((pixel >> 4) & 0x0F) * 255) / 15
							r = (((pixel >> 0) & 0x0F) * 255)/ 15

						rgba = (r << 0) | (g << 8) | (b << 16) | (a << 24)
						out[(y1 * w) + x1] = rgba
		return ''.join(Struct.uint32(p) for p in out)
	def RGB565(self, (w, h), jar):
		out = [0 for i in range(w * h)]
		i = 0
		for y in range(0, h, 4):
			for x in range(0, w, 4):
				for y1 in range(y, y + 4):
					for x1 in range(x, x + 4):
						if(y1 >= h or x1 >= w):
							continue
						pixel = Struct.uint16(jar[i * 2:i * 2 + 2], endian='>')
						i += 1
						
						b = (((pixel >> 11) & 0x1F) << 3) & 0xff
						g = (((pixel >> 5) & 0x3F) << 2) & 0xff
						r = (((pixel >> 0) & 0x1F) << 3) & 0xff
						a = 255

						rgba = (r << 0) | (g << 8) | (b << 16) | (a << 24)
						out[y1 * w + x1] = rgba
		return ''.join(Struct.uint32(p) for p in out)
	def I4(self, (w, h), jar):
		out = [0 for i in range(w * h)]
		i = 0
		for y in range(0, h, 8):
			for x in range(0, w, 8):
				for y1 in range(y, y + 8):
					for x1 in range(x, x + 8, 2):
						if(y1 >= h or x1 >= w):
							continue
						pixel = jar[i]
						
						r = (pixel >> 4) * 255 / 15
						g = (pixel >> 4) * 255 / 15
						b = (pixel >> 4) * 255 / 15
						a = 255

						rgba = (r << 0) | (g << 8) | (b << 16) | (a << 24)
						out[y1 * w + x1] = rgba
						
						if(y1 >= h or x1 >= w):
							continue
						pixel = jar[i]
						i += 1
						
						r = (pixel & 0x0F) * 255 / 15
						g = (pixel & 0x0F) * 255 / 15
						b = (pixel & 0x0F) * 255 / 15
						a = 255

						rgba = (r << 0) | (g << 8) | (b << 16) | (a << 24)
						out[y1 * w + x1 + 1] = rgba
		return ''.join(Struct.uint32(p) for p in out)
	def IA4(self, (w, h), jar):
		out = [0 for i in range(w * h)]
		i = 0
		for y in range(0, h, 4):
			for x in range(0, w, 8):
				for y1 in range(y, y + 4):
					for x1 in range(x, x + 8):
						if(y1 >= h or x1 >= w):
							continue
						pixel = jar[i]
						i += 1
						
						r = ((pixel & 0x0F) * 255 / 15) & 0xff
						g = ((pixel & 0x0F) * 255 / 15) & 0xff
						b = ((pixel & 0x0F) * 255 / 15) & 0xff
						a = (((pixel >> 4) * 255) / 15) & 0xff

						rgba = ( r<< 0) | (g << 8) | (b << 16) | (a << 24)
						out[y1 * w + x1] = rgba
		return ''.join(Struct.uint32(p) for p in out)
	def I8(self, (w, h), jar):
		out = [0 for i in range(w * h)]
		i = 0
		for y in range(0, h, 4):
			for x in range(0, w, 8):
				for y1 in range(y, y + 4):
					for x1 in range(x, x + 8):
						if(y1 >= h or x1 >= w):
							continue
						pixel = jar[i]
						i += 1
						
						r = pixel
						g = pixel
						b = pixel
						a = 255

						rgba = (r << 0) | (g << 8) | (b << 16) | (a << 24)
						out[y1 * w + x1] = rgba
		return ''.join(Struct.uint32(p) for p in out)
	def IA8(self, (w, h), jar):
		out = [0 for i in range(w * h)]
		i = 0
		for y in range(0, h, 4):
			for x in range(0, w, 4):
				for y1 in range(y, y + 4):
					for x1 in range(x, x + 4):
						if(y1 >= h or x1 >= w):
							continue
						pixel = Struct.uint16(jar[i * 2:i * 2 + 2], endian='>')
						i += 1
						
						r = (pixel >> 8) & 0xff
						g = (pixel >> 8) & 0xff
						b = (pixel >> 8) & 0xff
						a = pixel  & 0xff

						rgba = (r << 0) | (g << 8) | (b << 16) | (a << 24)
						out[y1 * w + x1] = rgba
		return ''.join(Struct.uint32(p) for p in out)
	def CI4(self, (w, h), jar, pal):
		out = [0 for i in range(w * h)]
		i = 0
		for y in range(0, h, 8):
			for x in range(0, w, 8):
				for y1 in range(y, y + 8):
					for x1 in range(x, x + 8, 2):
						if(y1 >= h or x1 >= w):
							continue
						pixel = jar[i]
						
						r = (pal[pixel] & 0xFF000000) >> 24
						g = (pal[pixel] & 0x00FF0000) >> 16
						b = (pal[pixel] & 0x0000FF00) >> 8
						a = (pal[pixel] & 0x000000FF) >> 0

						rgba = (r << 0) | (g << 8) | (b << 16) | (a << 24)
						out[y1 * w + x1] = rgba
						
						if(y1 >= h or x1 >= w):
							continue
						pixel = jar[i]
						i += 1
						
						r = (pal[pixel] & 0xFF000000) >> 24
						g = (pal[pixel] & 0x00FF0000) >> 16
						b = (pal[pixel] & 0x0000FF00) >> 8
						a = (pal[pixel] & 0x000000FF) >> 0

						rgba = (r << 0) | (g << 8) | (b << 16) | (a << 24)
						out[y1 * w + x1 + 1] = rgba
		return ''.join(Struct.uint32(p) for p in out)
	def CI8(self, (w, h), jar, pal):
		out = [0 for i in range(w * h)]
		i = 0
		for y in range(0, h, 4):
			for x in range(0, w, 8):
				for y1 in range(y, y + 4):
					for x1 in range(x, x + 8):
						if(y1 >= h or x1 >= w):
							continue
						pixel = jar[i]
						i += 1
						
						r = (pal[pixel] & 0xFF000000) >> 24
						g = (pal[pixel] & 0x00FF0000) >> 16
						b = (pal[pixel] & 0x0000FF00) >> 8
						a = (pal[pixel] & 0x000000FF) >> 0

						rgba = (r << 0) | (g << 8) | (b << 16) | (a << 24)
						out[y1 * w + x1] = rgba
		return ''.join(Struct.uint32(p) for p in out)
	def CMP(self, (w, h), data):
		temp = [0 for i in range(w * h)]
		pix = [ 0 , 0 , 0 ]
		c = [ 0 , 0 , 0 , 0 ]
		outp = 0
		for y in xrange(h):
			for x in xrange(w):
				ww = round_up(w, 8)

				x0 = x & 0x03
				x1 = (x >> 2) & 0x01
				x2 = x >> 3

				y0 = y & 0x03
				y1 = (y >> 2) & 0x01
				y2 = y >> 3

				off = (8 * x1) + (16 * y1) + (32 * x2) + (4 * ww * y2)

				c[0] = Struct.uint16(data[off + 0:off + 2], endian='>')
				c[1] = Struct.uint16(data[off + 2:off + 4], endian='>')
				if(c[0] > c[1]):
					c[2] = avg(2, 1, c[0], c[1])
					c[3] = avg(1, 2, c[0], c[1])
				else:
					c[2] = avg(1, 1, c[0], c[1])
					c[3] = 0

				px = Struct.uint32(data[off+4:off + 8], endian='>')
				ix = x0 + ( 4 * y0 )
				raw = c[(px >> (30 - (2 * ix))) & 0x03]

				pix[0] = (raw >> 8) & 0xf8
				pix[1] = (raw >> 3) & 0xf8
				pix[2] = (raw << 3) & 0xf8

				temp[outp] = (pix[0] <<0) | (pix[1] << 8) | (pix[2] << 16) | (255 << 24)
				outp += 1
		return ''.join(Struct.uint32(p) for p in temp)
	def CI14X2(self, (w, h), jar):
		out = [0 for i in range(w * h)]
		i = 0
		for y in range(0, h, 4):
			for x in range(0, w, 4):
				for y1 in range(y, y + 4):
					for x1 in range(x, x + 4):
						if(y1 >= h or x1 >= w):
							continue
						pixel = jar[i]
						i += 1
						
						r = (pal[pixel & 0x3FFF] & 0xFF000000) >> 24
						g = (pal[pixel & 0x3FFF] & 0x00FF0000) >> 16
						b = (pal[pixel & 0x3FFF] & 0x0000FF00) >> 8
						a = (pal[pixel & 0x3FFF] & 0x000000FF) >> 0

						rgba = (r << 0) | (g << 8) | (b << 16) | (a << 24)
						out[y1 * w + x1] = rgba
		return ''.join(Struct.uint32(p) for p in out)
