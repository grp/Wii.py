#!/usr/bin/python

import sys, struct

from Struct import Struct

def nullterm(str_plus):
	z = str_plus.find('\0')
	if z != -1:
		return str_plus[:z]
	else:
		return str_plus

class BREFF(object):
	class BREFF_REFF_StringSection1(Struct):
		__endian__ = Struct.BE
		def __format__(self):
			self.offset = Struct.uint32
			self.length = Struct.uint32
		def __str__(self):
			return_string  = "Offset: %08x\n" % self.offset
			return_string += "Length: %08x\n" % self.length
			return return_string

	class BREFF_REFF(Struct):
		__endian__ = Struct.BE
		def __format__(self):
			self.magic = Struct.string(4)
			self.length = Struct.uint32
			self.chunk_cnt = Struct.uint32
		def __str__(self):
			return_string  = "Magic: %s\n" % self.magic
			return_string += "Length: %08x\n" % self.length
			return_string += "Chunk Count: %08x\n" % self.chunk_cnt
			return return_string

	class BREFF_Header(Struct):
		__endian__ = Struct.BE
		def __format__(self):
			self.magic = Struct.string(4)
			self.version = Struct.uint32
			self.length = Struct.uint32
			self.header_size = Struct.uint16
			self.chunk_cnt = Struct.uint16
		def __str__(self):
			return_string  = "Magic: %s\n" % self.magic
			return_string += "Version: %08x\n" % self.version
			return_string += "Length: %08x\n" % self.length
			return_string += "Header Size: %04x\n" % self.header_size
			return_string += "Chunk Count: %04x\n" % self.chunk_cnt
			return return_string

	def __init__(self, data):
		self.data = []
		if data != None:
			self.Unpack(data)

	def Unpack(self, data):
		pos = 0
		header = self.BREFF_Header()
		header.unpack(data[pos:pos+len(header)])
		pos += len(header)
		print header
		assert header.magic == "REFF"
		assert header.version == 0xfeff0004
		reff = self.BREFF_REFF()
		reff.unpack(data[pos:pos+len(reff)])
		pos += len(reff)
		print reff
		assert reff.magic == "REFF"
		
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown: %08x" % unknown
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown: %08x" % unknown
		str_length = Struct.uint16(data[pos:pos+2], endian='>')
		pos += 2
		print "String Length with null added: %04x" % str_length
		unknown = Struct.uint16(data[pos:pos+2], endian='>')
		pos += 2
		print "Unknown: %04x" % unknown
		string = data[pos:pos+str_length-1]
		pos += str_length + (2 - (str_length % 2))
		print "String: %s\n" % string

		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Offset or Length: %08x" % unknown

		print "\n%08x\n" % pos

		string_cnt = Struct.uint16(data[pos:pos+2], endian='>')
		pos += 2
		print "String Count: %04x" % string_cnt
		unknown = Struct.uint16(data[pos:pos+2], endian='>')
		pos += 2
		print "Unknown: %04x" % unknown

		print "\n%08x\n" % pos

		for x in xrange(string_cnt):
			str_length = Struct.uint16(data[pos:pos+2], endian='>')
			pos += 2
			print "String Length with null added: %04x" % str_length
			string = nullterm(data[pos:pos+str_length])
			pos += str_length 
			print "String: %s" % string
			string_section1 = self.BREFF_REFF_StringSection1()
			string_section1.unpack(data[pos:pos+len(string_section1)])
			pos += len(string_section1)
			print string_section1

		print "\n%08x\n" % pos

		while pos % 0x10:
			padding = Struct.uint8(data[pos:pos+1])
			pos += 1
			print "Padding: %02x" % padding

		print "\n%08x\n" % pos

#		for x in xrange(string_cnt):
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown01: %08x" % unknown
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown02: %08x" % unknown
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown03: %08x" % unknown
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown04: %08x" % unknown
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown05: %08x" % unknown
		unknown = Struct.float(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown06: %f" % unknown
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown07: %08x" % unknown
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown08: %08x" % unknown
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown09: %08x" % unknown
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown10: %08x" % unknown
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown11: %08x" % unknown
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown12: %08x" % unknown
		unknown = Struct.float(data[pos:pos+4], endian='>')
		pos += 4
		print "PI TIMES 2 BITCHES: %.20f" % unknown
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown14: %08x" % unknown
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown15: %08x" % unknown
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown16: %08x" % unknown
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown17: %08x" % unknown
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown18: %08x" % unknown
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown19: %08x" % unknown
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown20: %08x" % unknown
		unknown = Struct.float(data[pos:pos+4], endian='>')
		pos += 4
		print "PI DIVIDED BY 4 BITCHES: %.20f" % unknown
		unknown = Struct.float(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown22: %f" % unknown
		unknown = Struct.float(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown23: %f" % unknown
		unknown = Struct.float(data[pos:pos+4], endian='>')
		pos += 4
		print "PI BITCHES: %.20f" % unknown
		unknown = Struct.float(data[pos:pos+4], endian='>')
		pos += 4
		print "PI DIVIDED BY 2 BITCHES: %.20f" % unknown
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown26: %08x" % unknown
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown27: %08x" % unknown
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown28: %08x" % unknown
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown29: %08x" % unknown
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown30: %08x" % unknown
		unknown = Struct.float(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown31: %f" % unknown
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown32: %08x" % unknown
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown33: %08x" % unknown
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown34: %08x" % unknown
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown35: %08x" % unknown
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown36: %08x" % unknown
		unknown = Struct.float(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown37: %f" % unknown
		unknown = Struct.float(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown38: %f" % unknown
		unknown = Struct.float(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown39: %f" % unknown
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown40: %08x" % unknown
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown41: %08x" % unknown
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown42: %08x" % unknown
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown43: %08x" % unknown
		unknown = Struct.float(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown44: %.20f" % unknown
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown45: %08x" % unknown
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown46: %08x" % unknown
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown47: %08x" % unknown
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown48: %08x" % unknown
			#pass

		#''' BEGIN TEST DATA  
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
	if len(sys.argv) != 2:
		print 'Usage: python breff.py <filename>'
		sys.exit(1)

	f = open(sys.argv[1], 'rb')
	if f:
		reff = f.read()
		f.close()
		assert reff[0:8] == 'REFF\xfe\xff\x00\x04'
		breff = BREFF(reff)
	else:
		print 'Could not open %s' % sys.argv[1]
		sys.exit(1)

if __name__ == "__main__":
	main()
