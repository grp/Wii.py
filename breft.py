#!/usr/bin/python

import sys, struct

from Struct import Struct

def nullterm(str_plus):
	z = str_plus.find('\0')
	if z != -1:
		return str_plus[:z]
	else:
		return str_plus

class BREFT(object):
	class BREFT_REFT_Section2(Struct):
		__endian__ = Struct.BE
		def __format__(self):
			self.unknown00 = Struct.uint32
			self.unknown01 = Struct.uint32
			self.unknown02 = Struct.uint32
			self.unknown03 = Struct.uint32
			self.unknown04 = Struct.uint32
			self.unknown05 = Struct.uint32
			self.unknown06 = Struct.uint32
			self.unknown07 = Struct.uint32
			self.unknown08 = Struct.uint32
			self.unknown09 = Struct.uint32
			self.unknown10 = Struct.uint32
			self.unknown11 = Struct.uint32
			self.unknown12 = Struct.uint32
			self.unknown13 = Struct.uint32
			self.unknown14 = Struct.uint32
			self.unknown15 = Struct.uint32
			self.unknown16 = Struct.uint32
			self.unknown17 = Struct.uint32
			self.unknown18 = Struct.uint32
			self.unknown19 = Struct.uint32
			self.unknown20 = Struct.uint32
			self.unknown21 = Struct.uint32
			self.unknown22 = Struct.uint32
			self.unknown23 = Struct.uint32
			self.unknown24 = Struct.uint32
			self.unknown25 = Struct.uint32
			self.unknown26 = Struct.uint32
			self.unknown27 = Struct.uint32
			self.unknown28 = Struct.uint32
			self.unknown29 = Struct.uint32
			self.unknown30 = Struct.uint32
			self.unknown31 = Struct.uint32
			self.unknown32 = Struct.uint32
			self.unknown33 = Struct.uint32
			self.unknown34 = Struct.uint32
			self.unknown35 = Struct.uint32
			self.unknown36 = Struct.uint32
			self.unknown37 = Struct.uint32
			self.unknown38 = Struct.uint32
			self.unknown39 = Struct.uint32
			self.unknown40 = Struct.uint32
			self.unknown41 = Struct.uint32
			self.unknown42 = Struct.uint32
			self.unknown43 = Struct.uint32
			self.unknown44 = Struct.uint32
			self.unknown45 = Struct.uint32
			self.unknown46 = Struct.uint32
			self.unknown47 = Struct.uint32
			self.unknown48 = Struct.uint32
			self.unknown49 = Struct.uint32
			self.unknown50 = Struct.uint32
			self.unknown51 = Struct.uint32
			self.unknown52 = Struct.uint32
			self.unknown53 = Struct.uint32
			self.unknown54 = Struct.uint32
			self.unknown55 = Struct.uint32
			self.unknown56 = Struct.uint32
			self.unknown57 = Struct.uint32
			self.unknown58 = Struct.uint32
			self.unknown59 = Struct.uint32
			self.unknown60 = Struct.uint32
			self.unknown61 = Struct.uint32
			self.unknown62 = Struct.uint32
			self.unknown63 = Struct.uint32
			self.unknown64 = Struct.uint32
			self.unknown65 = Struct.uint32
			self.unknown66 = Struct.uint32
			self.unknown67 = Struct.uint32
			self.unknown68 = Struct.uint32
			self.unknown69 = Struct.uint32
			self.unknown70 = Struct.uint32
			self.unknown71 = Struct.uint32
			self.unknown72 = Struct.uint32
			self.unknown73 = Struct.uint32
			self.unknown74 = Struct.uint32
			self.unknown75 = Struct.uint32
			self.unknown76 = Struct.uint32
			self.unknown77 = Struct.uint32
			self.unknown78 = Struct.uint32
			self.unknown79 = Struct.uint32
			self.unknown80 = Struct.uint32
			self.unknown81 = Struct.uint32
			self.unknown82 = Struct.uint32
			self.unknown83 = Struct.uint32
			self.unknown84 = Struct.uint32
			self.unknown85 = Struct.uint32
			self.unknown86 = Struct.uint32
			self.unknown87 = Struct.uint32
			self.unknown88 = Struct.uint32
			self.unknown89 = Struct.uint32
			self.unknown90 = Struct.uint32
			self.unknown91 = Struct.uint32
			self.unknown92 = Struct.uint32
			self.unknown93 = Struct.uint32
			self.unknown94 = Struct.uint32
			self.unknown95 = Struct.uint32
			self.unknown96 = Struct.uint32
			self.unknown97 = Struct.uint32
			self.unknown98 = Struct.uint32
			self.unknown99 = Struct.uint32
			self.unknownA0 = Struct.uint32
			self.unknownA1 = Struct.uint32
			self.unknownA2 = Struct.uint32
			self.unknownA3 = Struct.uint32
			self.unknownA4 = Struct.uint32
			self.unknownA5 = Struct.uint32
			self.unknownA6 = Struct.uint32
			self.unknownA7 = Struct.uint32
			self.unknownA8 = Struct.uint32
			self.unknownA9 = Struct.uint32
			self.unknownB0 = Struct.uint32
			self.unknownB1 = Struct.uint32
			self.unknownB2 = Struct.uint32
			self.unknownB3 = Struct.uint32
			self.unknownB4 = Struct.uint32
			self.unknownB5 = Struct.uint32
			self.unknownB6 = Struct.uint32
			self.unknownB7 = Struct.uint32
			self.unknownB8 = Struct.uint32
			self.unknownB9 = Struct.uint32
			self.unknownC0 = Struct.uint32
			self.unknownC1 = Struct.uint32
			self.unknownC2 = Struct.uint32
			self.unknownC3 = Struct.uint32
			self.unknownC4 = Struct.uint32
			self.unknownC5 = Struct.uint32
			self.unknownC6 = Struct.uint32
			self.unknownC7 = Struct.uint32
		def __str__(self):
			return_string  = "Unknown00: %08x\n" % self.unknown00
			return_string += "Unknown01: %08x\n" % self.unknown01
			return_string += "Unknown02: %08x\n" % self.unknown02
			return_string += "Unknown03: %08x\n" % self.unknown03
			return_string += "Unknown04: %08x\n" % self.unknown04
			return_string += "Unknown05: %08x\n" % self.unknown05
			return_string += "Unknown06: %08x\n" % self.unknown06
			return_string += "Unknown07: %08x\n" % self.unknown07
			return_string += "Unknown08: %08x\n" % self.unknown08
			return_string += "Unknown09: %08x\n" % self.unknown09
			return_string += "Unknown10: %08x\n" % self.unknown10
			return_string += "Unknown11: %08x\n" % self.unknown11
			return_string += "Unknown12: %08x\n" % self.unknown12
			return_string += "Unknown13: %08x\n" % self.unknown13
			return_string += "Unknown14: %08x\n" % self.unknown14
			return_string += "Unknown15: %08x\n" % self.unknown15
			return_string += "Unknown16: %08x\n" % self.unknown16
			return_string += "Unknown17: %08x\n" % self.unknown17
			return_string += "Unknown18: %08x\n" % self.unknown18
			return_string += "Unknown19: %08x\n" % self.unknown19
			return_string += "Unknown20: %08x\n" % self.unknown20
			return_string += "Unknown21: %08x\n" % self.unknown21
			return_string += "Unknown22: %08x\n" % self.unknown22
			return_string += "Unknown23: %08x\n" % self.unknown23
			return_string += "Unknown24: %08x\n" % self.unknown24
			return_string += "Unknown25: %08x\n" % self.unknown25
			return_string += "Unknown26: %08x\n" % self.unknown26
			return_string += "Unknown27: %08x\n" % self.unknown27
			return_string += "Unknown28: %08x\n" % self.unknown28
			return_string += "Unknown29: %08x\n" % self.unknown29
			return_string += "Unknown30: %08x\n" % self.unknown30
			return_string += "Unknown31: %08x\n" % self.unknown31
			return_string += "Unknown32: %08x\n" % self.unknown32
			return_string += "Unknown33: %08x\n" % self.unknown33
			return_string += "Unknown34: %08x\n" % self.unknown34
			return_string += "Unknown35: %08x\n" % self.unknown35
			return_string += "Unknown36: %08x\n" % self.unknown36
			return_string += "Unknown37: %08x\n" % self.unknown37
			return_string += "Unknown38: %08x\n" % self.unknown38
			return_string += "Unknown39: %08x\n" % self.unknown39
			return_string += "Unknown40: %08x\n" % self.unknown40
			return_string += "Unknown41: %08x\n" % self.unknown41
			return_string += "Unknown42: %08x\n" % self.unknown42
			return_string += "Unknown43: %08x\n" % self.unknown43
			return_string += "Unknown44: %08x\n" % self.unknown44
			return_string += "Unknown45: %08x\n" % self.unknown45
			return_string += "Unknown46: %08x\n" % self.unknown46
			return_string += "Unknown47: %08x\n" % self.unknown47
			return_string += "Unknown48: %08x\n" % self.unknown48
			return_string += "Unknown49: %08x\n" % self.unknown49
			return_string += "Unknown50: %08x\n" % self.unknown50
			return_string += "Unknown51: %08x\n" % self.unknown51
			return_string += "Unknown52: %08x\n" % self.unknown52
			return_string += "Unknown53: %08x\n" % self.unknown53
			return_string += "Unknown54: %08x\n" % self.unknown54
			return_string += "Unknown55: %08x\n" % self.unknown55
			return_string += "Unknown56: %08x\n" % self.unknown56
			return_string += "Unknown57: %08x\n" % self.unknown57
			return_string += "Unknown58: %08x\n" % self.unknown58
			return_string += "Unknown59: %08x\n" % self.unknown59
			return_string += "Unknown60: %08x\n" % self.unknown60
			return_string += "Unknown61: %08x\n" % self.unknown61
			return_string += "Unknown62: %08x\n" % self.unknown62
			return_string += "Unknown63: %08x\n" % self.unknown63
			return_string += "Unknown64: %08x\n" % self.unknown64
			return_string += "Unknown65: %08x\n" % self.unknown65
			return_string += "Unknown66: %08x\n" % self.unknown66
			return_string += "Unknown67: %08x\n" % self.unknown67
			return_string += "Unknown68: %08x\n" % self.unknown68
			return_string += "Unknown69: %08x\n" % self.unknown69
			return_string += "Unknown70: %08x\n" % self.unknown70
			return_string += "Unknown71: %08x\n" % self.unknown71
			return_string += "Unknown72: %08x\n" % self.unknown72
			return_string += "Unknown73: %08x\n" % self.unknown73
			return_string += "Unknown74: %08x\n" % self.unknown74
			return_string += "Unknown75: %08x\n" % self.unknown75
			return_string += "Unknown76: %08x\n" % self.unknown76
			return_string += "Unknown77: %08x\n" % self.unknown77
			return_string += "Unknown78: %08x\n" % self.unknown78
			return_string += "Unknown79: %08x\n" % self.unknown79
			return_string += "Unknown80: %08x\n" % self.unknown80
			return_string += "Unknown81: %08x\n" % self.unknown81
			return_string += "Unknown82: %08x\n" % self.unknown82
			return_string += "Unknown83: %08x\n" % self.unknown83
			return_string += "Unknown84: %08x\n" % self.unknown84
			return_string += "Unknown85: %08x\n" % self.unknown85
			return_string += "Unknown86: %08x\n" % self.unknown86
			return_string += "Unknown87: %08x\n" % self.unknown87
			return_string += "Unknown88: %08x\n" % self.unknown88
			return_string += "Unknown89: %08x\n" % self.unknown89
			return_string += "Unknown90: %08x\n" % self.unknown90
			return_string += "Unknown91: %08x\n" % self.unknown91
			return_string += "Unknown92: %08x\n" % self.unknown92
			return_string += "Unknown93: %08x\n" % self.unknown93
			return_string += "Unknown94: %08x\n" % self.unknown94
			return_string += "Unknown95: %08x\n" % self.unknown95
			return_string += "Unknown96: %08x\n" % self.unknown96
			return_string += "Unknown97: %08x\n" % self.unknown97
			return_string += "Unknown98: %08x\n" % self.unknown98
			return_string += "Unknown99: %08x\n" % self.unknown99
			return_string += "UnknownA0: %08x\n" % self.unknownA0
			return_string += "UnknownA1: %08x\n" % self.unknownA1
			return_string += "UnknownA2: %08x\n" % self.unknownA2
			return_string += "UnknownA3: %08x\n" % self.unknownA3
			return_string += "UnknownA4: %08x\n" % self.unknownA4
			return_string += "UnknownA5: %08x\n" % self.unknownA5
			return_string += "UnknownA6: %08x\n" % self.unknownA6
			return_string += "UnknownA7: %08x\n" % self.unknownA7
			return_string += "UnknownA8: %08x\n" % self.unknownA8
			return_string += "UnknownA9: %08x\n" % self.unknownA9
			return_string += "UnknownB0: %08x\n" % self.unknownB0
			return_string += "UnknownB1: %08x\n" % self.unknownB1
			return_string += "UnknownB2: %08x\n" % self.unknownB2
			return_string += "UnknownB3: %08x\n" % self.unknownB3
			return_string += "UnknownB4: %08x\n" % self.unknownB4
			return_string += "UnknownB5: %08x\n" % self.unknownB5
			return_string += "UnknownB6: %08x\n" % self.unknownB6
			return_string += "UnknownB7: %08x\n" % self.unknownB7
			return_string += "UnknownB8: %08x\n" % self.unknownB8
			return_string += "UnknownB9: %08x\n" % self.unknownB9
			return_string += "UnknownC0: %08x\n" % self.unknownC0
			return_string += "UnknownC1: %08x\n" % self.unknownC1
			return_string += "UnknownC2: %08x\n" % self.unknownC2
			return_string += "UnknownC3: %08x\n" % self.unknownC3
			return_string += "UnknownC4: %08x\n" % self.unknownC4
			return_string += "UnknownC5: %08x\n" % self.unknownC5
			return_string += "UnknownC6: %08x\n" % self.unknownC6
			return_string += "UnknownC7: %08x\n" % self.unknownC7
			return return_string

	class BREFT_REFT_StringSection1(Struct):
		__endian__ = Struct.BE
		def __format__(self):
			self.offset = Struct.uint32
			self.length = Struct.uint32
		def __str__(self):
			return_string  = "Offset: %08x\n" % self.offset
			return_string += "Length: %08x\n" % self.length
			return return_string

	class BREFT_REFT_StringHeader(Struct):
		__endian__ = Struct.BE
		def __format__(self):
			self.offset = Struct.uint16
			self.length = Struct.uint16
			self.string_cnt = Struct.uint16
			self.unknown01 = Struct.uint16
		def __str__(self):
			return_string  = "Offset: %04x\n" % self.offset
			return_string += "Offset: %04x\n" % self.length
			return_string += "String Count: %04x\n" % self.string_cnt
			return_string += "Unknown01: %04x" % self.unknown01
			return return_string

	class BREFT_REFT_Project(Struct):
		__endian__ = Struct.BE
		def __format__(self):
			self.length = Struct.uint32
			self.unknown01 = Struct.uint32
			self.unknown02 = Struct.uint32
			self.str_length = Struct.uint16
			self.unknown03 = Struct.uint16
		def __str__(self):
			return_string  = "Length: %08x\n" % self.length
			return_string += "Unknown01: %08x\n" % self.unknown01
			return_string += "Unknown02: %08x\n" % self.unknown02
			return_string += "Number of Strings: %04x\n" % self.str_length
			return_string += "Unknown: %04x" % self.unknown03
			return return_string

	class BREFT_REFT(Struct):
		__endian__ = Struct.BE
		def __format__(self):
			self.magic = Struct.string(4)
			self.length = Struct.uint32
		def __str__(self):
			return_string  = "Magic: %s\n" % self.magic
			return_string += "Length: %08x\n" % self.length
			return return_string

	class BREFT_Header(Struct):
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
		header = self.BREFT_Header()
		header.unpack(data[pos:pos+len(header)])
		pos += len(header)
		print header
		assert header.magic == "REFT"
		assert header.version == 0xfeff0004
		reft = self.BREFT_REFT()
		reft.unpack(data[pos:pos+len(reft)])
		pos += len(reft)
		print reft
		assert reft.magic == "REFT"
		
		print "\n%08x\n" % pos

		reft_project = self.BREFT_REFT_Project()
		reft_project.unpack(data[pos:pos+len(reft_project)])
		pos += len(reft_project)
		print reft_project
		string = nullterm(data[pos:pos+reft_project.str_length])
		pos += reft_project.str_length
		print "String: %s\n" % string

		while pos %2:
			unknown = Struct.uint8(data[pos:pos+1])
			pos += 1
			print "Padding: %02x" % unknown

		print "\n%08x\n" % pos

		for x in xrange(0x30):
			pad = Struct.uint8(data[pos:pos+1])
			pos += 1
			#print "Padding: %08x" % pad

		print "\n%08x\n" % pos
		temp = pos

		reft_string_header = self.BREFT_REFT_StringHeader()
		reft_string_header.unpack(data[pos:pos+len(reft_string_header)])
		pos += len(reft_string_header)
		print reft_string_header

		print "\n%08x\n" % pos

		string_groups = []
		for x in xrange(reft_string_header.string_cnt):
			str_length = Struct.uint16(data[pos:pos+2], endian='>')
			pos += 2
			print "String Length with null added: %04x" % str_length
			string = nullterm(data[pos:pos+str_length])
			pos += str_length
			print "String: %s" % string
			string_section1 = self.BREFT_REFT_StringSection1()
			string_section1.unpack(data[pos:pos+len(string_section1)])
			pos += len(string_section1)
			print string_section1
			string_groups.append(string_section1)

		for x in xrange(reft_string_header.string_cnt):
			pos = temp + string_groups[x].offset
			print "\n%08x\n" % pos
			reft_section2 = self.BREFT_REFT_Section2()
			reft_section2.unpack(data[pos:pos+len(reft_section2)])
			pos += len(reft_section2)
			print reft_section2

		print "\n%08x\n" % pos

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
		print 'Usage: python breft.py <filename>'
		sys.exit(1)

	f = open(sys.argv[1], 'rb')
	if f:
		reft = f.read()
		f.close()
		assert reft[0:8] == 'REFT\xfe\xff\x00\x04'
		breft = BREFT(reft)
	else:
		print 'Could not open %s' % sys.argv[1]
		sys.exit(1)

if __name__ == "__main__":
	main()
