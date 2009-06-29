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
	class BREFF_REFF_Section2(Struct):
		__endian__ = Struct.BE
		def __format__(self):
			self.unknown01 = Struct.uint32
			self.unknown02 = Struct.uint32
			self.unk03p1 = Struct.uint16
			self.unk03p2 = Struct.uint16
			self.unk04p1 = Struct.int16
			self.unk04p2 = Struct.uint16
			self.unknown05 = Struct.uint32
			self.unknown06 = Struct.float
			self.unknown07 = Struct.uint32
			self.unknown08 = Struct.uint32
			self.unknown09 = Struct.uint32
			self.unknown10 = Struct.float
			self.unknown11 = Struct.float
			self.unknown12 = Struct.uint32
			self.unknown13 = Struct.float
			self.unknown14 = Struct.uint32
			self.unknown15 = Struct.uint32
			self.unk16p1 = Struct.uint16
			self.unk16p2 = Struct.uint16
			self.unknown17 = Struct.float
			self.unknown18 = Struct.float
			self.unknown19 = Struct.uint32
			self.unknown20 = Struct.float
			self.unknown21 = Struct.float
			self.unknown22 = Struct.float
			self.unknown23 = Struct.float
			self.unknown24 = Struct.float
			self.unknown25 = Struct.float
			self.unknown26 = Struct.uint32
			self.unknown27 = Struct.uint32
			self.unknown28 = Struct.uint32
			self.unknown29 = Struct.uint32
			self.unknown30 = Struct.uint32
			self.unknown31 = Struct.float
			self.unknown32 = Struct.uint32
			self.unknown33 = Struct.uint32
			self.unknown34 = Struct.uint32
			self.unknown35 = Struct.uint32
			self.unknown36 = Struct.uint32
			self.unknown37 = Struct.float
			self.unknown38 = Struct.float
			self.unknown39 = Struct.float
			self.unknown40 = Struct.float
			self.unknown41 = Struct.float
			self.unknown42 = Struct.uint32
			self.unknown43 = Struct.uint32
			self.unknown44 = Struct.float
			self.unknown45 = Struct.uint32
			self.unknown46 = Struct.uint32
			self.unknown47 = Struct.uint32
			self.unknown48 = Struct.uint32
		def __str__(self):
			return_string  = "Unknown01: %08x\talways 00000128 ?\n" % self.unknown01
			return_string += "Unknown02: %08x\talways 80000xxx ?\n" % self.unknown02
			return_string += "Unknown03: %04x\t%04x\n" % (self.unk03p1 , self.unk03p2)
			return_string += "Unknown04: %.2d\t%04x\n" % (self.unk04p1 , self.unk04p2)
			return_string += "Unknown05: %08x\n" % self.unknown05
			return_string += "Unknown06: %.9f\n" % self.unknown06
			return_string += "Unknown07: %08x\n" % self.unknown07
			return_string += "Unknown08: %08x\n" % self.unknown08
			return_string += "Unknown09: %08x\n" % self.unknown09
			return_string += "Unknown10: %.9f\n" % self.unknown10
			return_string += "Unknown11: %.9f\n" % self.unknown11
			return_string += "Unknown12: %08x\n" % self.unknown12
			return_string += "Unknown13: %.9f\n" % self.unknown13
			return_string += "Unknown14: %08x\n" % self.unknown14
			return_string += "Unknown15: %08x\n" % self.unknown15
			return_string += "Unknown16: %04x\t%04x\n" % (self.unk16p1, self.unk16p2)
			return_string += "Unknown17: %.9f\n" % self.unknown17
			return_string += "Unknown18: %.9f\n" % self.unknown18
			return_string += "Unknown19: %08x\n" % self.unknown19
			return_string += "Unknown20: %.9f\n" % self.unknown20
			return_string += "Unknown21: %.9f\n" % self.unknown21
			return_string += "Unknown22: %08x\n" % self.unknown22
			return_string += "Unknown23: %08x\n" % self.unknown23
			return_string += "Unknown24: %.20f\n" % self.unknown24
			return_string += "Unknown25: %.9f\n" % self.unknown25
			return_string += "Unknown26: %08x\n" % self.unknown26
			return_string += "Unknown27: %08x\n" % self.unknown27
			return_string += "Unknown28: %08x\n" % self.unknown28
			return_string += "Unknown29: %08x\n" % self.unknown29
			return_string += "Unknown30: %08x\n" % self.unknown30
			return_string += "Unknown31: %.9f\n" % self.unknown31
			return_string += "Unknown32: %08x\n" % self.unknown32
			return_string += "Unknown33: %08x\n" % self.unknown33
			return_string += "Unknown34: %08x\n" % self.unknown34
			return_string += "Unknown35: %08x\n" % self.unknown35
			return_string += "Unknown36: %08x\n" % self.unknown36
			return_string += "Unknown37: %.9f\n" % self.unknown37
			return_string += "Unknown38: %.9f\n" % self.unknown38
			return_string += "Unknown39: %.9f\n" % self.unknown39
			return_string += "Unknown40: %.9f\n" % self.unknown40
			return_string += "Unknown41: %.9f\n" % self.unknown41
			return_string += "Unknown42: %08x\n" % self.unknown42
			return_string += "Unknown43: %08x\n" % self.unknown43
			return_string += "Unknown44: %.9f\n" % self.unknown44
			return_string += "Unknown45: %08x\n" % self.unknown45
			return_string += "Unknown46: %08x\n" % self.unknown46
			return_string += "Unknown47: %08x\n" % self.unknown47
			return_string += "Unknown48: %08x\n" % self.unknown48
			return return_string

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

		string_groups = []
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
			string_groups.append(string_section1)

		print "\n%08x\n" % pos

		while pos % 0x10:
			padding = Struct.uint8(data[pos:pos+1])
			pos += 1
			print "Padding: %02x" % padding

		print "\n%08x\n" % pos

		assert pos == string_groups[0].offset + 0x34
		for x in xrange(string_cnt):
			pos = 0x34 + string_groups[x].offset
			reff_section2 = self.BREFF_REFF_Section2()
			reff_section2.unpack(data[pos:pos+len(reff_section2)])
			pos += len(reff_section2)
			print reff_section2

		''' LARGE TEST DATA
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
		LARGE TEST DATA '''

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
