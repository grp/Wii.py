#!/usr/bin/python

import sys, re, struct

from Struct import Struct

def nullterm(str_plus):
    z = str_plus.find('\x00\x22')
    if z != -1:
        return str_plus[:z]
    else:
        return str_plus
        
class CSV(object):
	def __init__(self, data):
		self.data = []
		if data != None:
			self.Unpack(data)

	def Unpack(self, data):
		pos = 0x4a

		while pos < len(data):
			string = nullterm(data[pos:])
			string = unicode(string, 'utf_16_be')
			print "String: %s" % string
			pos += len(string) * 2 + 6

def main():
	if len(sys.argv) == 1:
		print 'Usage: python csv.py <filename>'
		sys.exit(1)
	f = open(sys.argv[1], 'rb')
	if f:
		csv_buffer = f.read()
		f.close()
	else:
		print 'Could not open file for reading'
		sys.exit(1)

	csv = CSV(csv_buffer)

if __name__ == "__main__":
	main()
