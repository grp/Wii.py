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
    z = str_plus.find('\x0a')
    if z != -1:
        return str_plus[:z]
    else:
        return str_plus
        
class ZND(object):
	def __init__(self, data=None, out_file=None, debug=False):
		self.data = []
		if data != None:
			self.Unpack(data, out_file, debug)

	def Unpack(self, data, out_file, debug=False):
		file = open(out_file, 'wb')
		if file:
			pos = 0

			count = Struct.uint32(data[pos:pos+4], endian='>')
			pos += 4
			if debug == True:
				print "Count: %08x" % count
				print "\n%08x\n" % pos

			offset_list = []
			for x in xrange(count):
				offset = Struct.uint32(data[pos:pos+4], endian='>')
				pos += 4
				if debug == True:
					print "Offset: %08x" % offset
				offset_list.append(offset)

			if debug == True:
				print "\n%08x\n" % pos

			for x in xrange(count):
				pos = offset_list[x]
				string = nullterm(data[pos:])
				string = unicode(string, 'utf_16_be')
				if debug == True:
					print "String: %s" % string.encode('utf-8')
				pos += len(string)
				file.write(string.encode('utf-8'))
				file.write('\n')
			file.close()
		else:
			print "Could not open file for writing"
			sys.exit(1)

	def write(self, data, out_file):
		file = open(out_file, 'wb')
		if file:
			pos = 0
			count = 0
			string_list = []
			while pos < len(data):
				temp = denullterm(data[pos:])
				pos += len(temp) + 1
				string = unicode(temp, 'utf-8')
				string_list.append(string)
				count += 1
			file.write(struct.pack('>I', count))
			pos = count * 4 + 4
			for x in xrange(count):
				file.write(struct.pack('>I', pos))
				pos += len(string_list[x]) * 2 + 2
			for x in xrange(count):
				file.write(string_list[x].encode('utf_16_be'))
				file.write('\x00\x00')
			while pos % 0x20:
				pos += 2
				file.write('\x00\x00')
			file.close()
		else:
			print "Could not open file for writing"
			sys.exit(1)

def main():
	if len(sys.argv) == 1:
		print 'Usage: python znd.py -r <filename.znd> <filename.hog>'
		print '                 == OR ==                            '
		print 'Usage: python znd.py -w <filename.hog> <filename.znd>'
		sys.exit(1)
	if sys.argv[1] == "-r":
		f = open(sys.argv[2], 'rb')
		if f:
			znd_buffer = f.read()
			f.close()
		else:
			print 'Could not open file for reading'
			sys.exit(1)
		znd = ZND(znd_buffer, sys.argv[3], debug=False)
	elif sys.argv[1] == "-w":
		f = open(sys.argv[2], 'rb')
		if f:
			buffer = f.read()
			f.close()
		else:
			print 'Could not open file for reading'
			sys.exit(1)
		znd = ZND()
		znd.write(buffer, sys.argv[3])
	else:
		print 'Usage: python znd.py -r <filename.znd> <filename.hog>'
		print '                 == OR ==                            '
		print 'Usage: python znd.py -w <filename.hog> <filename.znd>'
		sys.exit(1)

if __name__ == "__main__":
	main()
