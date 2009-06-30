#!/usr/bin/python

import sys, re, struct

from Struct import Struct

def nullterm(str_plus):
    z = str_plus.find('\x00\x00')
    if z != -1:
        return str_plus[:z]
    else:
        return str_plus
        
class ZND(object):
	def __init__(self, data):
		self.data = []
		if data != None:
			self.Unpack(data)

	def Unpack(self, data):
		pos = 0

		count = Struct.uint32(data[pos:pos+4], endian='>')
		pos += 4
		print "Count: %08x" % count

		print "\n%08x\n" % pos

		offset_list = []
		for x in xrange(count):
			offset = Struct.uint32(data[pos:pos+4], endian='>')
			pos += 4
			print "Offset: %08x" % offset
			offset_list.append(offset)

		print "\n%08x\n" % pos

		for x in xrange(count):
			pos = offset_list[x]
			string = nullterm(data[pos:])
			string = unicode(string, 'utf_16_be')
			print "String: %s" % string
			pos += len(string)

def main():
	if len(sys.argv) == 1:
		print 'Usage: python bmg.py'
		sys.exit(1)
	f = open(sys.argv[1], 'rb')
	if f:
		znd_buffer = f.read()
		f.close()
	else:
		print 'Could not open file for reading'
		sys.exit(1)

	znd = ZND(znd_buffer)

if __name__ == "__main__":
	main()
