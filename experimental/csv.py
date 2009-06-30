#!/usr/bin/python

import sys, re, struct

from Struct import Struct

hardstring  = '\xfe\xff\x00\x22\x63\xa5\x7d\x9a\x30\x59\x30\x8b\x98\x06\x75\x6a'
hardstring += '\x30\x6b\x00\x0d\x00\x0a\x24\x60\x30\xdc\x30\xbf\x30\xf3\x30\x68'

def nullterm(str_plus):
    z = str_plus.find('\x00\x09')
    if z != -1:
        return str_plus[:z]
    else:
        return str_plus
        
def denullterm(str_plus):
    z = str_plus.find('\x0a\x0a')
    if z != -1:
        return str_plus[:z]
    else:
        return str_plus
        
class CSV(object):
	def __init__(self, data=None, outfile=None, debug=False):
		self.data = []
		if data != None:
			self.Unpack(data, outfile, debug)

	def Unpack(self, data, outfile=None, debug=False):
		if outfile != None:
			file = open(outfile, 'wb')

		pos = 0

		version = Struct.uint16(data[pos:pos+2], endian='>')
		pos += 2
		if debug == True:
			print "Version: %04x" % version
			print

		self.string_list = []
		while pos < len(data):
			string = nullterm(data[pos:])
			string = unicode(string, 'utf_16_be')
			if debug == True:
				print "String: %s" % string
			pos += len(string) * 2 + 2
			self.string_list.append(string)
			file.write(string.encode('utf-8'))
			file.write('\n')
			if pos < len(data):
				file.write('\n')

		file.close()

	def write(self, data, output_file):
		file = open(output_file, 'wb')
		if file:
			file.write('\xfe\xff')

			pos = 0
			while pos < len(data):
				temp = denullterm(data[pos:])
				pos += len(temp) + 2
				string = unicode(temp, 'utf-8')
				file.write(string.encode('utf_16_be'))

				if pos < len(data):
					file.write('\x00\x09')
				else:
					file.write('\x00\x0a')

			file.close()
		else:
			print "Could not open file for writing"
			sys.exit(1)

def main():
	if len(sys.argv) == 1:
		print 'Usage: python -r csv.py <filename.csv> <filename.hog>'
		print '                  == OR ==                           '
		print 'Usage: python -w csv.py <filename.hog> <filename.csv>'
		sys.exit(1)
	if sys.argv[1] == "-r":
		f = open(sys.argv[2], 'rb')
		if f:
			csv_buffer = f.read()
			f.close()
		else:
			print 'Could not open file for reading'
			sys.exit(1)
		csv = CSV(csv_buffer, outfile=sys.argv[3], debug=False)
	elif sys.argv[1] == "-w":
		f = open(sys.argv[2], 'rb')
		if f:
			input_file = f.read()
			f.close()
		else:
			print 'Could not open file for reading'
			sys.exit(1)
		csv = CSV()
		csv.write(input_file, sys.argv[3])
	else:
		print 'Usage: python -r csv.py <filename.csv> <filename.hog>'
		print '                  == OR ==                           '
		print 'Usage: python -w csv.py <filename.hog> <filename.csv>'
		sys.exit(1)

if __name__ == "__main__":
	main()
