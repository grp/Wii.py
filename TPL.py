import os, hashlib, struct, subprocess, fnmatch, shutil, urllib, array
import wx
from Crypto.Cipher import AES
import png
from Struct import Struct

class TPL():
	"""This is the class to generate TPL texutres from PNG images, and to convert TPL textures to PNG images. The parameter file specifies the filename of the source, either a PNG image or a TPL image.
	
	Currently supported are the following formats to convert from TPL: RGBA8, RGB565, RGB5A3, I4, I8, IA4, IA8. Currently not supported are: CI4, CI8, CMP.
	
	Currently support to convert to TPL: RGBA8. Currently not supported are: RGB565, RGB5A3, I4, I8, IA4, IA8, CI4, CI8, CMP.
	
	There are still some bugs in either the RGBA8 conversion to or from TPL. This causes stretched and distorted images with some files and images dimensions."""
	
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
			self.pallete_offset = Struct.uint32
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
	def __init__(self, file):
		self.file = file
	def toTPL(self, outfile, width = 0, height = 0): #single texture only
		"""This converts a PNG image into a TPL. The PNG image is specified as the file parameter to the class initializer, while the output filename is specified here as the parameter outfile. Width and height are optional parameters and specify the size to resize the image to, if needed. Returns the output filename.
		
		This only can create TPL images with a single texture."""
		head = self.TPLHeader()
		head.magic = 0x0020AF30
		head.ntextures = 1
		head.header_size = 0x0C
		
		tex = self.TPLTexture()
		tex.header_offset = 0x14
		tex.pallete_offset = 0
		
		img = wx.Image(self.file, wx.BITMAP_TYPE_ANY)
		if(width !=0 and height != 0 and (width != img.GetWidth() or height != img.GetHeight())):
			img.Rescale(width, height)
		w = img.GetWidth()
		h = img.GetHeight()
		
		texhead = self.TPLTextureHeader()
		texhead.height = h
		texhead.width = w
		texhead.format = 6
		texhead.data_off = 0x14 + len(texhead) + 8
		texhead.wrap = [0, 0]
		texhead.filter = [1, 1]
		texhead.lod_bias = 0
		texhead.edge_lod = 0
		texhead.min_lod = 0
		texhead.max_lod = 0
		texhead.unpacked = 0
		
		tpldata = self.toRGBA8((w, h), img, img.HasAlpha())
		
		f = open(outfile, "wb")
		f.write(head.pack())
		f.write(tex.pack())
		f.write(texhead.pack())
		f.write(struct.pack(">" + str(align(w, 4) * align(h, 4) * 4) + "B", *tpldata))
		f.close()
		
		return outfile
		
	def toRGBA8(self, (w, h), img, alpha):
		out = [0 for i in range(align(w, 4) * align(h, 4) * 4)]
		i = z = 0
		lr = la = lb = lg = [0 for i in range(32)]
		for y in range(0, h, 4):
			for x in range(0, w, 4):
				for y1 in range(y, y + 4):
					for x1 in range(x, x + 4):
						if(y1 >= h or x1 >= w):
							lr[z] = lg[z] = lb[z] = la[z] = 0
						else:
							lr[z] = img.GetRed(x1, y1)
							lg[z] = img.GetGreen(x1, y1)
							lb[z] = img.GetBlue(x1, y1)
							if(alpha == True):
								la[z] = img.GetAlpha(x1, y1)
							else:
								la[z] = 255
						z += 1
				
				if(z == 16):
					for iv in range(16):
						out[i] = lr[iv]
						i += 1
						out[i] = la[iv]
						i += 1
					for iv in range(16):
						out[i] = lb[iv]
						i += 1
						out[i] = lg[iv]
						i += 1
					z = 0
		return out
	def toPNG(self, outfile): #single texture only
		"""This converts a TPL texture to a PNG image. You specify the input TPL filename in the initializer, and you specify the output filename in the outfile parameter to this method. Returns the output filename.
		
		This only supports single textured TPL images."""
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
				tpldata = struct.unpack(">" + str(w * h) + "H", data[tex.data_off:tex.data_off + (w * h * 2)])
				rgbdata = self.RGB565((w, h), tpldata)
			elif(tex.format == 5): #RGB5A3, 16-bit
				tpldata = struct.unpack(">" + str(w * h) + "H", data[tex.data_off:tex.data_off + (w * h * 2)])
				rgbdata = self.RGB5A3((w, h), tpldata)
			elif(tex.format == 3): #IA8, 16-bit
				tpldata = struct.unpack(">" + str(w * h) + "H", data[tex.data_off:tex.data_off + (w * h * 2)])
				rgbdata = self.IA8((w, h), tpldata)
			
			elif(tex.format == 6): #RGBA8, 32-bit, but for easyness's sake lets do it with 16-bit
				tpldata = struct.unpack(">" + str(w * h * 2) + "H", data[tex.data_off:tex.data_off + (w * h * 4)])
				rgbdata = self.RGBA8((w, h), tpldata)
				
			else:
				raise TypeError("Unsupported TPL Format: " + str(tex.format))
		
		output = png.Writer(width = w, height = h, alpha = True, bitdepth = 8)
		output.write(open(outfile, "wb"), rgbdata)
		
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
		class imp(wx.Panel):
			def __init__(self, parent, id, im):
				wx.Panel.__init__(self, parent, id)
				w = im.GetWidth()
				h = im.GetHeight()
				wx.StaticBitmap(self, -1, im, ( ((max(w, 300) - w) / 2), ((max(h, 200) - h) / 2) ), (w, h))

		self.toPNG("tmp.png")
		img = wx.Image("tmp.png", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
		w = img.GetWidth()
		h = img.GetHeight()
		app = wx.App(redirect = True)
		frame = wx.Frame(None, -1, "TPL (" + str(w) + ", " + str(h) + ")", size = (max(w, 300), max(h, 200)))
		image = imp(frame, -1, img)
		frame.Show(True)
		app.MainLoop()
		os.unlink("tmp.png")
	def RGBA8(self, (w, h), jar):
		out = [[0 for i in range(w * 4)] for i in range(h)]
		i = 0
		for y in range(0, h, 4):
			for x in range(0, w, 4):
				for iv in range(2):
					for y1 in range(y, y + 4):
						for x1 in range(x, x + 4):
							if(y1 >= h or x1 >= w):
								continue
							pixel = jar[i]
							i += 1
							
							if(iv == 0):
								r = (pixel >> 0) & 0xFF
								a = (pixel >> 8) & 0xFF
								out[y1][(x1 * 4) + 0] = r
								out[y1][(x1 * 4) + 3] = a
							else:
								g = (pixel >> 8) & 0xFF
								b = (pixel >> 0) & 0xFF
								out[y1][(x1 * 4) + 1] = g
								out[y1][(x1 * 4) + 2] = b
		return out
	def RGB5A3(self, (w, h), jar):
		out = [[0 for i in range(w * 4)] for i in range(h)]
		i = 0
		for y in range(0, h, 4):
			for x in range(0, w, 4):
				for y1 in range(y, y + 4):
					for x1 in range(x, x + 4):
						if(y1 >= h or x1 >= w):
							continue
						pixel = jar[i]
						i += 1
						
						if(pixel & (1 << 15)): #RGB555
							r = (((pixel >> 10) & 0x1F) * 255) / 31
							g = (((pixel >> 5) & 0x1F) * 255) / 31
							b = (((pixel >> 0) & 0x1F) * 255) / 31
							a = 255
						else: #RGB4A3
							r = (((pixel >> 8) & 0x0F) * 255) / 15
							g = (((pixel >> 4) & 0x0F) * 255) / 15
							b = (((pixel >> 0) & 0x0F) * 255) / 15
							a = 255 - (((pixel >> 12) & 0x07) * 64) / 7

						out[y1][(x1 * 4) + 0] = r
						out[y1][(x1 * 4) + 1] = g
						out[y1][(x1 * 4) + 2] = b
						out[y1][(x1 * 4) + 3] = a
		return out
	def RGB565(self, (w, h), jar):
		out = [[0 for i in range(w * 4)] for i in range(h)]
		i = 0
		for y in range(0, h, 4):
			for x in range(0, w, 4):
				for y1 in range(y, y + 4):
					for x1 in range(x, x + 4):
						if(y1 >= h or x1 >= w):
							continue
						pixel = jar[i]
						i += 1
						
						r = ((pixel >> 11) & 0x1F) << 3
						g = ((pixel >> 5) & 0x3F) << 2
						b = ((pixel >> 0) & 0x1F) << 3
						a = 255

						out[y1][(x1 * 4) + 0] = r
						out[y1][(x1 * 4) + 1] = g
						out[y1][(x1 * 4) + 2] = b
						out[y1][(x1 * 4) + 3] = a
		return out
	def I4(self, (w, h), jar):
		out = [[0 for i in range(w * 4)] for i in range(h)]
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

						out[y1][(x1 * 4) + 0] = r
						out[y1][(x1 * 4) + 1] = g
						out[y1][(x1 * 4) + 2] = b
						out[y1][(x1 * 4) + 3] = a
						
						if(y1 >= h or x1 >= w):
							continue
						pixel = jar[i]
						i += 1
						
						r = (pixel & 0x0F) * 255 / 15
						g = (pixel & 0x0F) * 255 / 15
						b = (pixel & 0x0F) * 255 / 15
						a = 255

						out[y1][((x1 + 1) * 4) + 0] = r
						out[y1][((x1 + 1) * 4) + 1] = g
						out[y1][((x1 + 1) * 4) + 2] = b
						out[y1][((x1 + 1) * 4) + 3] = a
		return out
	def IA4(self, (w, h), jar):
		out = [[0 for i in range(w * 4)] for i in range(h)]
		i = 0
		for y in range(0, h, 4):
			for x in range(0, w, 8):
				for y1 in range(y, y + 4):
					for x1 in range(x, x + 8):
						if(y1 >= h or x1 >= w):
							continue
						pixel = jar[i]
						i += 1
						
						r = (pixel & 0x0F) * 255 / 15
						g = (pixel & 0x0F) * 255 / 15
						b = (pixel & 0x0F) * 255 / 15
						a = 255 - ((pixel & 0xFF) * 255 / 15)

						out[y1][(x1 * 4) + 0] = r
						out[y1][(x1 * 4) + 1] = g
						out[y1][(x1 * 4) + 2] = b
						out[y1][(x1 * 4) + 3] = a
		return out
	def I8(self, (w, h), jar):
		out = [[0 for i in range(w * 4)] for i in range(h)]
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

						out[y1][(x1 * 4) + 0] = r
						out[y1][(x1 * 4) + 1] = g
						out[y1][(x1 * 4) + 2] = b
						out[y1][(x1 * 4) + 3] = a
		return out
	def IA8(self, (w, h), jar):
		out = [[0 for i in range(w * 4)] for i in range(h)]
		i = 0
		for y in range(0, h, 4):
			for x in range(0, w, 4):
				for y1 in range(y, y + 4):
					for x1 in range(x, x + 4):
						if(y1 >= h or x1 >= w):
							continue
						pixel = jar[i]
						i += 1
						
						r = pixel >> 8
						g = pixel >> 8
						b = pixel >> 8
						a = 255 - (pixel & 0xFF)

						out[y1][(x1 * 4) + 0] = r
						out[y1][(x1 * 4) + 1] = g
						out[y1][(x1 * 4) + 2] = b
						out[y1][(x1 * 4) + 3] = a
		return out

