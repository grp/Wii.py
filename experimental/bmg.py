#!/usr/bin/python

import sys, re, struct

from Struct import Struct

def nullterm(str_plus):
    z = str_plus.find('\x00\x00')
    if z != -1:
        return str_plus[:z]
    else:
        return str_plus
        
def denullterm(str_plus):
    z = str_plus.find('\r\n')
    if z != -1:
        return str_plus[:z]
    else:
        return str_plus
        
class BMG(object):
	class BMG_DAT1(Struct):
		__endian__ = Struct.BE
		def __format__(self):
			self.magic = Struct.string(4)
			self.length = Struct.uint32
		def __str__(self):
			return_string  = "Magic: %s\n" % self.magic
			return_string += "Length: %08x\n " % self.length
			return return_string
		def write(self, file):
			file.write(self.magic)
			file.write(struct.pack('>I', self.length))
			return

	class BMG_INF1(Struct):
		__endian__ = Struct.BE
		def __format__(self):
			self.magic = Struct.string(4)
			self.length = Struct.uint32
			self.count = Struct.uint16
			self.unknown01 = Struct.uint16
		def __str__(self):
			return_string  = "Magic: %s\n" % self.magic
			return_string += "Length: %08x\n " % self.length
			return_string += "Count: %04x\n" % self.count
			return_string += "Unknown: %04x\n" % self.unknown01
			return return_string
		def write(self, file):
			file.write(self.magic)
			file.write(struct.pack('>I', self.length))
			file.write(struct.pack('>H', self.count))
			file.write(struct.pack('>H', self.unknown01))
			return

	class BMG_Header(Struct):
		__endian__ = Struct.BE
		def __format__(self):
			self.magic = Struct.string(4)
			self.magic2 = Struct.string(4)
			self.length = Struct.uint32
			self.chunk_cnt = Struct.uint32
			self.unknown01 = Struct.uint8
			self.unknown02 = Struct.uint8
			self.unknown03 = Struct.uint16
			self.unknown04 = Struct.uint32
			self.unknown05 = Struct.uint32
			self.unknown06 = Struct.uint32
		def __str__(self):
			return_string  = "Magic: %s\n" % self.magic
			return_string += "Magic: %s\n" % self.magic2
			return_string += "Length: %08x\n" % self.length
			return_string += "Chunk Count: %08x\n" % self.chunk_cnt
			return_string += "Unknown01: %02x\n" % self.unknown01
			return_string += "Unknown02: %02x\n" % self.unknown02
			return_string += "Unknown03: %04x\n" % self.unknown03
			return_string += "Unknown04: %08x\n" % self.unknown04
			return_string += "Unknown05: %08x\n" % self.unknown05
			return_string += "Unknown06: %08x\n" % self.unknown06
			return return_string
		def write(self, file):
			file.write(self.magic)
			file.write(self.magic2)
			file.write(struct.pack('>I', self.length))
			file.write(struct.pack('>I', self.chunk_cnt))
			file.write(struct.pack('>B', self.unknown01))
			file.write(struct.pack('>B', self.unknown02))
			file.write(struct.pack('>H', self.unknown03))
			file.write(struct.pack('>I', self.unknown04))
			file.write(struct.pack('>I', self.unknown05))
			file.write(struct.pack('>I', self.unknown06))
			return

	def __init__(self, data=None, out_file=None, debug=False):
		self.data = []
		if data != None:
			self.Unpack(data, out_file, debug)

	def Unpack(self, data, out_file, debug):
		file = open(out_file, 'wb')
		if file:
			pos = 0
			header = self.BMG_Header()
			header.unpack(data[pos:pos+len(header)])
			pos += len(header)
			if debug == True:
				print header
				print "\n%08x\n" % pos

			info = self.BMG_INF1()
			info.unpack(data[pos:pos+len(info)])
			pos += len(info)
			if debug == True:
				print info

			unknown = Struct.uint32(data[pos:pos+4], endian='>')
			pos += 4
			if debug == True:
				print "Unknown: %08x" % unknown
				print "\n%08x\n" % pos

			offset_list = []
			for x in xrange(info.count):
				offset = Struct.uint32(data[pos:pos+4], endian='>')
				pos +=  4
				if debug == True:
					print "Offset: %08x" % offset
				offset_list.append(offset)

			while pos % 0x10:
				padding = Struct.uint32(data[pos:pos+4], endian='>')
				pos += 4
				if debug == True:
					print "Padding: %08x" % padding

			if debug == True:
				print "\n%08x\n" % pos

			dat1 = self.BMG_DAT1()
			dat1.unpack(data[pos:pos+len(dat1)])
			pos += len(dat1)
			if debug == True:
				print dat1

			if debug == True:
				print "\n%08x\n" % pos
			temp = pos

			unknown = Struct.uint16(data[pos:pos+2], endian='>')
			pos += 2
			if debug == True:
				print "Unknown: %04x" % unknown

			for x in xrange(info.count):
				pos = temp + offset_list[x]
				string = nullterm(data[pos:])
				string = unicode(string, 'utf_16_be')
				file.write(string.encode('utf-8'))
				file.write('\r')
				file.write('\n')
				if debug == True:
					print "String: %s" % string.encode('utf-8')
			file.close()
		else:
			print "Could not open file for writing"
			sys.exit(1)
	def write(self, data, out_file):
		file = open(out_file, 'wb')
		if file:
			pos = 0
			count = 0
			strings_list = []
			while pos < len(data):
				temp = denullterm(data[pos:])
				pos += len(temp) + 2
				string = unicode(temp, 'utf-8')
				strings_list.append(string)
				count += 1
			offsets_list = []
			offset = 2
			for x in xrange(count):
				offsets_list.append(offset)
				offset += len(strings_list[x]) * 2 + 2
			dat1 = self.BMG_DAT1()
			dat1.length = offset + 8 + (0x10 - (offset % 0x10))
			dat_pad_to_add = 0x10 - (offset % 0x10)
			info = self.BMG_INF1()
			info.length = 0x10 + 4 * count + (0x10 - ((4 * count) % 0x10))
			info_pad_to_add = 0x10 - ((4*count) % 0x10)
			header = self.BMG_Header()
			header.magic = "MESG"
			header.magic2 = "bmg1"
			header.length = info.length + dat1.length + 0x20
			header.chunk_cnt = 2
			header.unknown01 = 2
			header.unknown02 = 0
			header.unknown03 = 0
			header.unknown04 = 0
			header.unknown05 = 0
			header.unknown06 = 0
			header.write(file)
			info.magic = "INF1"
			info.count = count
			info.unknown01 = 4
			info.write(file)
			unknown = 0
			file.write(struct.pack('>I', unknown))
			offset_list = []
			for x in offsets_list:
				file.write(struct.pack('>I', x))
			padding = 0
			for x in xrange(info_pad_to_add):
				file.write(struct.pack('>B', padding))
			dat1.magic = "DAT1"
			dat1.write(file)
			unknown = 0
			file.write(struct.pack('>H', unknown))
			for x in strings_list:
				file.write(x.encode('utf_16_be'))
				file.write('\x00\x00')
			file.write("\n")
			padding = 0
			for x in xrange(dat_pad_to_add):
				file.write(struct.pack('>B', padding))
			file.close()
		else:
			print "Could not open file for writing"
			sys.exit(1)

def main():
	if len(sys.argv) == 1:
		print 'Usage: python bmg.py -r <filename.bmg> <filename.hog>'
		print '                  == OR ==                           '
		print 'Usage: python bmg.py -w> <filename.hog> <filename.bmg'
		sys.exit(1)
	if sys.argv[1] == "-r":
		f = open(sys.argv[2], 'rb')
		if f:
			bmg_buffer = f.read()
			f.close()
		else:
			print 'Could not open file for reading'
			sys.exit(1)
		bmg = BMG(bmg_buffer, sys.argv[3], debug=False)
	elif sys.argv[1] == "-w":
		f = open(sys.argv[2], 'rb')
		if f:
			bmg_buffer = f.read()
			f.close()
		else:
			print "Could not open file for reading"
			sys.exit(1)
		bmg = BMG()
		bmg.write(bmg_buffer, sys.argv[3])

if __name__ == "__main__":
	main()
