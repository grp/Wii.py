#!/usr/bin/python

import sys, re, struct

from Struct import Struct

def nullterm(str_plus):
    z = str_plus.find('\x00\x00')
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

	def __init__(self, data):
		self.data = []
		if data != None:
			self.Unpack(data)

	def Unpack(self, data):
		pos = 0
		header = self.BMG_Header()
		header.unpack(data[pos:pos+len(header)])
		pos += len(header)
		print header

		print "\n%08x\n" % pos

		info = self.BMG_INF1()
		info.unpack(data[pos:pos+len(info)])
		pos += len(info)
		print info

		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown: %08x" % unknown

		print "\n%08x\n" % pos

		offset_list = []
		for x in xrange(info.count):
			offset = Struct.uint32(data[pos:pos+4], endian='>')
			pos +=  4
			print "Offset: %08x" % offset
			offset_list.append(offset)

		while pos % 0x10:
			padding = Struct.uint32(data[pos:pos+4], endian='>')
			pos += 4
			print "Padding: %08x" % padding

		print "\n%08x\n" % pos

		dat1 = self.BMG_DAT1()
		dat1.unpack(data[pos:pos+len(dat1)])
		pos += len(dat1)
		print dat1

		print "\n%08x\n" % pos
		temp = pos

		unknown = Struct.uint16(data[pos:pos+2], endian='>')
		pos += 2
		print "Unknown: %04x" % unknown

		for x in xrange(info.count):
			pos = temp + offset_list[x]
			string = nullterm(data[pos:])
			string = unicode(string, 'utf_16_be')
			print "String: %s" % string

		#''' TEST DATA
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown: %08x" % unknown
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown: %08x" % unknown
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown: %08x" % unknown
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown: %08x" % unknown
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown: %08x" % unknown
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown: %08x" % unknown
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown: %08x" % unknown
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown: %08x" % unknown
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown: %08x" % unknown
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown: %08x" % unknown
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown: %08x" % unknown
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown: %08x" % unknown
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown: %08x" % unknown
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown: %08x" % unknown
		#END TEST DATA '''

def main():
	if len(sys.argv) == 1:
		print 'Usage: python bmg.py'
		sys.exit(1)
	f = open(sys.argv[1], 'rb')
	if f:
		bmg_buffer = f.read()
		f.close()
	else:
		print 'Could not open file for reading'
		sys.exit(1)

	bmg = BMG(bmg_buffer)

if __name__ == "__main__":
	main()
