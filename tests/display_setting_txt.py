#!/uwr/bin/python

import sys, Wii

def main():
	settings = Wii.CONF(sys.argv[1])
	print settings.getKeysName()
	for x in settings.getKeysName():
		print settings.getKeyValue(x)
	sys.exit(0)

if __name__ == "__main__":
	main()
