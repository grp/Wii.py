import os, hashlib, struct, subprocess, fnmatch, shutil, urllib, array
import wx
import png

from Crypto.Cipher import AES
from Struct import Struct

from common import *



class TPL():
	"""This is the class to generate TPL texutres from PNG images, and to convert TPL textures to PNG images. The parameter file specifies the filename of the source, either a PNG image or a TPL image.
	
	Currently supported are the following formats to convert from TPL: RGBA8, RGB565, RGB5A3, CI4, CI8, I4, I8, IA4, IA8. Currently not supported are: CMP, CI14X2.
	
	Currently support to convert to TPL: RGBA8. Currently not supported, and are in the works, are: RGB565, RGB5A3, I4, I8, IA4, IA8, CI4, CI8, CMP, CI14X2.
	
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
				sz = ((w + 7) >> 3) * ((w + 7) >> 3) * 32
				#print sz
				#print len(data[tex.data_off:])
				tpldata = struct.unpack(">" + str(sz / 2) + "H", data[tex.data_off:tex.data_off + sz])
				
				rgbdata = self.CMP((w, h), tpldata)
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
	def RGBA8(self, (x, y), data):
		out = [[0 for i in range(x * 4)] for i in range(y)]
		inp = 0
		for i in xrange(0, y, 4):
			for j in xrange(0, x, 4):
				for k in xrange(2):
					for l in xrange(i, i + 4, 1):
						for m in xrange(j, j + 4, 1):
							texel = (data[inp])
							inp += 1
							if (m >= x) or (l >= y):
								continue
							if k == 0:
								a = (texel >> 8) & 0xff
								r = (texel >> 0) & 0xff
								out[l][(m*4)+0] = r
								out[l][(m*4)+3] = a
							else:
								g = (texel >> 8) & 0xff
								b = (texel >> 0) & 0xff
								out[l][(m*4)+1] = g
								out[l][(m*4)+2] = b
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
	def CI4(self, (w, h), jar, pal):
		out = [[0 for i in range(w * 4)] for i in range(h)]
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

						out[y1][(x1 * 4) + 0] = r
						out[y1][(x1 * 4) + 1] = g
						out[y1][(x1 * 4) + 2] = b
						out[y1][(x1 * 4) + 3] = a
						
						if(y1 >= h or x1 >= w):
							continue
						pixel = jar[i]
						i += 1
						
						r = (pal[pixel] & 0xFF000000) >> 24
						g = (pal[pixel] & 0x00FF0000) >> 16
						b = (pal[pixel] & 0x0000FF00) >> 8
						a = (pal[pixel] & 0x000000FF) >> 0

						out[y1][((x1 + 1) * 4) + 0] = r
						out[y1][((x1 + 1) * 4) + 1] = g
						out[y1][((x1 + 1) * 4) + 2] = b
						out[y1][((x1 + 1) * 4) + 3] = a
		return out
	def CI8(self, (w, h), jar, pal):
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
						
						r = (pal[pixel] & 0xFF000000) >> 24
						g = (pal[pixel] & 0x00FF0000) >> 16
						b = (pal[pixel] & 0x0000FF00) >> 8
						a = (pal[pixel] & 0x000000FF) >> 0

						out[y1][(x1 * 4) + 0] = r
						out[y1][(x1 * 4) + 1] = g
						out[y1][(x1 * 4) + 2] = b
						out[y1][(x1 * 4) + 3] = a
		return out
	def icolor(self, a, b, fa, fb, fc):
		c = 0
		for i in range(0, 32, 8):
			xa = (a >> i) & 0xff
			xb = (b >> i) & 0xff
			xc = min(255, max(0, int((xa * fa + xb * fb) / fc)))
			c |= xc << i
		return c
	def single565(self, pixel):
		r = ((pixel >> 11) & 0x1F) << 3
		g = ((pixel >> 5) & 0x3F) << 2
		b = ((pixel >> 0) & 0x1F) << 3
		a = 255
		return (r << 24) | (g << 16) | (b << 8) | (a << 0)
	def CMP(self, (w, h), jar):
		out = [[0 for i in range(w * 4)] for i in range(h)]
		
		pos = 0
		ofs = 0
		
		rgb = [0 for i in range(4)]
		dst = [0 for i in range(w * h)]
		for y in range(0, h, 8):
			for x in range(0, w, 8):
				maxw = min(w - x, 8)
				for k in range(2):
					for l in range(2):	
						rgb[0] = self.single565(jar[pos])
						pos += 1
						rgb[1] = self.single565(jar[pos])
						pos += 1

						if(jar[pos + 0] > jar[pos + 1]):
							rgb[2] = self.icolor(rgb[0], rgb[1], 2, 1, 3) | 0xFF000000
							rgb[3] = self.icolor(rgb[1], rgb[0], 2, 1, 3) | 0xFF000000
						else:
							rgb[2] = self.icolor(rgb[0], rgb[1], 0.5, 0.5, 1) | 0xFF000000
							#rgb[3] = self.icolor(rgb[1], rgb[0], 2, 1, 3) & ~0xFF000000
							rgb[3] = 0
							
						# color selection (00, 01, 10, 11)
						cm = jar[pos:pos + 2]
						pixels = []
						for pix in cm:
							pixels.append(pix >> 8)
							pixels.append(pix & 0xFF)
						pos += 2
						
						for n in range(4):
							# one row (4 texels)
							if(ofs < (w * h)):
								if(maxw > 0 + l * 4):
									dst[ofs] = rgb[(pixels[n] & 0xc0) >> 6]
									ofs += 1
								if(maxw > 1 + l * 4):
									dst[ofs] = rgb[(pixels[n] & 0x30) >> 4]
									ofs += 1
								if(maxw > 2 + l * 4):
									dst[ofs] = rgb[(pixels[n] & 0x0c) >> 2]
									ofs += 1
								if(maxw > 3 + l * 4):
									dst[ofs] = rgb[(pixels[n] & 0x03) >> 0]
									ofs += 1

		num_rows = 0
		num_tiles = 0
		for i in range(w * h):
			pixel = dst[i]
			
			tile_offset = i % 16 # where are we in the tile?
			if(i % 16 == 0 and i != 0): # if we are at the end of a tile...
				num_tiles += 1 # ...move on to the next one!

			if(num_tiles != 0 and (w / 4) == num_tiles): # if we are at the end of a row of tiles...
				num_tiles = 0 # ...reset!
				tile_offset = 0 # ...reset!
				num_rows += 4 # plus four because each tile is four high
				
			x = (tile_offset % 4) + (num_tiles * 4) # num_tiles part to not overwrite tiles earlier in this row, tile_offset to find how far on the x we are in this row in the tile
			y = (num_rows) + (tile_offset / 4) # num_rows to not overwrite tiles above, tile_offset to show how many rows in the current tile we are
			
			#print "tile %u of %u on row %u of %u (%u, %u): 0x%08x" % (num_tiles + 1, w / 4, (num_rows / 4) + 1, h / 4, x, y, pixel)
			
			r = (pixel & 0xFF000000) >> 24
			g = (pixel & 0x00FF0000) >> 16
			b = (pixel & 0x0000FF00) >> 8
			a = (pixel & 0x000000FF) >> 0
		
			out[y][(x * 4) + 0] = r
			out[y][(x * 4) + 1] = g
			out[y][(x * 4) + 2] = b
			out[y][(x * 4) + 3] = a		
		return out
	def CI14X2(self, (w, h), jar):
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
						
						r = (pal[pixel & 0x3FFF] & 0xFF000000) >> 24
						g = (pal[pixel & 0x3FFF] & 0x00FF0000) >> 16
						b = (pal[pixel & 0x3FFF] & 0x0000FF00) >> 8
						a = (pal[pixel & 0x3FFF] & 0x000000FF) >> 0

						out[y1][(x1 * 4) + 0] = r
						out[y1][(x1 * 4) + 1] = g
						out[y1][(x1 * 4) + 2] = b
						out[y1][(x1 * 4) + 3] = a
		return out