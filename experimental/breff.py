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
			self.unknown00 = Struct.uint32
			self.unknown01 = Struct.uint32
			self.unknown02 = Struct.uint32
			self.unk03p1 = Struct.uint16
			self.unk03p2 = Struct.uint16
			self.unk04p1 = Struct.int16
			self.unk04p2 = Struct.uint16
			self.unknown05 = Struct.uint32
			self.unknown06 = Struct.float
			self.unknown07 = Struct.float
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
			self.unknown81 = Struct.float
			self.unknown82 = Struct.float
			self.unknown83 = Struct.float
			self.unknown84 = Struct.float
			self.unknown85 = Struct.uint32
			self.unknown86 = Struct.uint32
			self.unknown87 = Struct.uint32
			self.unknown88 = Struct.float
			self.unknown89 = Struct.float
			self.unknown90 = Struct.float
			self.unknown91 = Struct.float
			self.unknown92 = Struct.float
			self.unknown93 = Struct.float
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
		def __str__(self):
			return_string  = "Unknown00: %08x\n" % self.unknown00
			return_string += "Unknown01: %08x\talways 00000128 ?\n" % self.unknown01
			return_string += "Unknown02: %08x\talways 80000xxx ?\n" % self.unknown02
			return_string += "Unknown03: %04x\t%04x\n" % (self.unk03p1 , self.unk03p2)
			return_string += "Unknown04: %.2d\t%04x\n" % (self.unk04p1 , self.unk04p2)
			return_string += "Unknown05: %08x\n" % self.unknown05
			return_string += "Unknown06: %.9f\n" % self.unknown06
			return_string += "Unknown07: %f\n" % self.unknown07
			return_string += "Unknown08: %08x\n" % self.unknown08
			return_string += "Unknown09: %08x\n" % self.unknown09
			return_string += "Size Outer Radius X: %.9f\n" % self.unknown10
			return_string += "Size Outer Radius Y: %.9f\n" % self.unknown11
			return_string += "Size Outer Radius Z: %.9f\n" % self.unknown12
			return_string += "Inner Radius: %.9f\n" % self.unknown13
			return_string += "Unknown14: %08x\n" % self.unknown14
			return_string += "Unknown15: %08x\n" % self.unknown15
			return_string += "Unknown16: %04x\t%04x\n" % (self.unk16p1, self.unk16p2)
			return_string += "All Direction Speed: %.9f\n" % self.unknown17
			return_string += "Y Axis Difuse Speed: %.9f\n" % self.unknown18
			return_string += "Random Direction Speed: %.9f\n" % self.unknown19
			return_string += "Normal Direction Speed: %.9f\n" % self.unknown20
			return_string += "Unknown21: %.9f\n" % self.unknown21
			return_string += "Move to Specific Direction: %.9f\n" % self.unknown22
			return_string += "Unknown23: %08x\n" % self.unknown23
			return_string += "Unknown24: %.20f\n" % self.unknown24
			return_string += "Unknown25: %.9f\n" % self.unknown25
			return_string += "Unknown26: %08x\n" % self.unknown26
			return_string += "Unknown27: %.9f\n" % self.unknown27
			return_string += "Unknown28: %.9f\n" % self.unknown28
			return_string += "Unknown29: %.9f\n" % self.unknown29
			return_string += "Unknown30: %08x\n" % self.unknown30
			return_string += "Unknown31: %.9f\n" % self.unknown31
			return_string += "Unknown32: %08x\n" % self.unknown32
			return_string += "Four Bytes: %08x\n" % self.unknown33
			return_string += "Unknown34: %08x\n" % self.unknown34
			return_string += "Unknown35: %08x\n" % self.unknown35
			return_string += "Unknown36: %08x\n" % self.unknown36
			return_string += "Transform Scale X: %.9f\n" % self.unknown37
			return_string += "Transform Scale Y: %.9f\n" % self.unknown38
			return_string += "Transform Scale Z: %.9f\n" % self.unknown39
			return_string += "Center of Particle SRT Horiz: %.9f\n" % self.unknown40
			return_string += "Center of Particle SRT Vert: %.9f\n" % self.unknown41
			return_string += "Unknown42: %08x\n" % self.unknown42
			return_string += "Unknown43: %08x\n" % self.unknown43
			return_string += "Unknown44: %.9f\n" % self.unknown44
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
			return_string += "Unknown81: %.9f\n" % self.unknown81
			return_string += "Unknown82: %.9f\n" % self.unknown82
			return_string += "Unknown83: %.9f\n" % self.unknown83
			return_string += "Unknown84: %.9f\n" % self.unknown84
			return_string += "Unknown85: %08x\n" % self.unknown85
			return_string += "Unknown86: %08x\n" % self.unknown86
			return_string += "Unknown87: %08x\n" % self.unknown87
			return_string += "Unknown88: %.9f\n" % self.unknown88
			return_string += "Unknown89: %.9f\n" % self.unknown89
			return_string += "Unknown90: %.9f\n" % self.unknown90
			return_string += "Unknown91: %.9f\n" % self.unknown91
			return_string += "Unknown92: %.9f\n" % self.unknown92
			return_string += "Unknown93: %.9f\n" % self.unknown93
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
		def __str__(self):
			return_string  = "Magic: %s\n" % self.magic
			return_string += "Length: %08x\n" % self.length
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
		
		temp = pos
		project = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Header Size: %08x" % project
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
		pos += str_length 
		print "String: %s\n" % string

		while pos % 2:
			unknown = Struct.uint8(data[pos:pos+1])
			pos += 1
			print "Padding: %02x" % unknown

		print "\n%08x\n" % pos
		temp = pos

		unknown = Struct.uint16(data[pos:pos+2], endian='>')
		pos += 2
		print "Offset: %04x" % unknown
		unknown = Struct.uint16(data[pos:pos+2], endian='>')
		pos += 2
		print "Length: %04x" % unknown

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

		while pos % 0x04:
			padding = Struct.uint8(data[pos:pos+1])
			pos += 1
			print "Padding: %02x" % padding

		print "\n%08x\n" % pos

		assert pos == string_groups[0].offset + temp
		for x in xrange(string_cnt):
			pos = temp + string_groups[x].offset
			reff_section2 = self.BREFF_REFF_Section2()
			reff_section2.unpack(data[pos:pos+len(reff_section2)])
			pos += len(reff_section2)
			print reff_section2
			print "\n%08x\n" % pos

		''' LARGE TEST DATA
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown01: %08x" % unknown
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown02: %08x" % unknown
		unknown = Struct.float(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown03: %f" % unknown
		unknown = Struct.float(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown04: %f" % unknown
		unknown = Struct.float(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown05: %f" % unknown
		unknown = Struct.float(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown06: %f" % unknown
		unknown = Struct.float(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown07: %f" % unknown
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown08: %08x" % unknown
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown09: %08x" % unknown
		unknown = Struct.float(data[pos:pos+4], endian='>')
		pos += 4
		print "Size Outer Radius X: %f" % unknown
		unknown = Struct.float(data[pos:pos+4], endian='>')
		pos += 4
		print "Size Outer Radius Y: %f" % unknown
		unknown = Struct.float(data[pos:pos+4], endian='>')
		pos += 4
		print "Size Outer Radius Z: %f" % unknown
		unknown = Struct.float(data[pos:pos+4], endian='>')
		pos += 4
		print "Inner Radius: %f" % unknown
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown14: %08x" % unknown
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown15: %08x" % unknown
		unknown = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown16: %08x" % unknown
		unknown = Struct.float(data[pos:pos+4], endian='>')
		pos += 4
		print "All Direction Speed: %f" % unknown
		unknown = Struct.float(data[pos:pos+4], endian='>')
		pos += 4
		print "Y Axis Difuse Speed: %f" % unknown
		unknown = Struct.float(data[pos:pos+4], endian='>')
		pos += 4
		print "Random Direction Speed: %f" % unknown
		unknown = Struct.float(data[pos:pos+4], endian='>')
		pos += 4
		print "Normal Direction Speed: %f" % unknown
		unknown = Struct.float(data[pos:pos+4], endian='>')
		pos += 4
		print "PI DIVIDED BY 4 BITCHES: %.20f" % unknown
		unknown = Struct.float(data[pos:pos+4], endian='>')
		pos += 4
		print "Move to specific direction: %f" % unknown
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
		unknown = Struct.float(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown27: %f" % unknown
		unknown = Struct.float(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown28: %f" % unknown
		unknown = Struct.float(data[pos:pos+4], endian='>')
		pos += 4
		print "Unknown29: %f" % unknown
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
		print "Bytes: %08x" % unknown
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
		print "Transform Scale X: %f" % unknown
		unknown = Struct.float(data[pos:pos+4], endian='>')
		pos += 4
		print "Transform Scale Y: %f" % unknown
		unknown = Struct.float(data[pos:pos+4], endian='>')
		pos += 4
		print "Transform Scale Z: %f" % unknown
		unknown = Struct.float(data[pos:pos+4], endian='>')
		pos += 4
		print "Center of Particle SRT Horizontal(x): %f" % unknown
		unknown = Struct.float(data[pos:pos+4], endian='>')
		pos += 4
		print "Center of Particle SRT Verticle(y): %f" % unknown
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

		''' BEGIN TEST DATA  
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
		END TEST DATA '''

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
