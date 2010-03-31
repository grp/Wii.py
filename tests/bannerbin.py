import Wii, os, sys, shutil

def packbanner():
	bannerbin = U8()
	bannerbin['arc'] = None #dir
	bannerbin['arc/blyt'] = None
	bannerbin['arc/anim'] = None
	bannerbin['arc/timg'] = None
	# then do
	origdir = os.getcwd()
	for files in os.walk(origdir + 'arc/timg/'):
		bannerbin['arc/timg/' + file] = open(file, "rb").read()
	for files in os.walk(origdir + 'arc/anim/'):
		bannerbin['arc/anim/' + file] = open(file, "rb").read()
	for files in os.walk(origdir + 'arc/blyt/'):
		bannerbin['arc/blyt/' + file] = open(file, "rb").read()
	fn = open("banner.bin", "w+b")
	fn.write(u8object.dumpFile())
	fn.close()



def doPack():
	exchange = [sys.argv[2], sys.argv[3], sys.argv[4]]
	global banneru8, iconu8
	
	print "Unpacking WAD..."
	wad = wii.WAD.loadFile("squid.wad")
	
	title = wii.IMET(wad[0]).getTitle()
	print "Unpacking 00000000.app..."
	wad[0] = wii.IMET(wad[0]).remove()
	
	meta = wii.U8.load(wad[0])

	prog = 20
	for i, item in enumerate(exchange):
		if(item == ""): #skip what doesn't get changed
			continue
		if(i == 0):
			bin = "banner"
			print "Replacing banner.bin..."
		elif(i == 1):
			bin = "icon"
			print "Replacing icon.bin..."
		else:
			bin = "sound"
			print "Replacing sound.bin..."
		
		if(item[len(item) - 3:] == "app" or item[len(item) - 3:] == "bnr" or item[len(item - 3):] == "wad"):
			if(item[len(item) - 3:] == "wad"):
				wad2 = wii.WAD.loadFile(item)
				wad2[0] = wii.IMET(wad2[0]).remove()
				meta2 = wii.U8.load(wad2[0])
			else:
				meta2 = wii.IMET.loadFile(item).remove()
			bin2 = meta2['meta/%s.bin' % bin]
		elif(item[len(item) - 3:] == "bin"):
			bin2 = wii.U8.loadFile(item)
		else:
			continue #only bin, wad, bnr and app are supported
		meta['arc/%s.bin' % bin] = bin2.dump()
	
	print "Unpacking banner.bin..."
	meta['meta/banner.bin'] = wii.IMD5(meta['meta/banner.bin']).remove()
	meta['meta/banner.bin'] = wii.LZ77(meta['meta/banner.bin']).remove()
	banneru8 = wii.U8.load(meta['meta/banner.bin'])

	print "Unpacking icon.bin..."
	meta['meta/icon.bin'] = wii.IMD5(meta['meta/icon.bin']).remove()
	meta['meta/icon.bin'] = wii.LZ77(meta['meta/icon.bin']).remove()
	iconu8 = wii.U8.load(meta['meta/icon.bin'])
	
	print "Packing banner.bin..."
	meta['meta/banner.bin'] = banneru8.dump()
	meta['meta/banner.bin'] = wii.IMD5(meta['meta/banner.bin']).add()
	
	print "Packing icon.bin..."
	meta['meta/icon.bin'] = iconu8.dump()
	meta['meta/icon.bin'] = wii.IMD5(meta['meta/icon.bin']).add()
	
	print "Packing 00000000.app..."

	#meta['meta/sound.bin'] = open('wadunpack/00000000_app_out/meta/sound.bin', 'rb').read()
	langs = []
	wad[0] = meta.dump()
	wad[0] = wii.IMET(wad[0]).add(len(meta['meta/icon.bin']), len(meta['meta/banner.bin']), len(meta['meta/sound.bin']), title, langs)
	
	print "Packing WAD..."
	wad.dumpFile("squid.wad")

def main():
	packbanner()
	doPack()

if __name__ == "__main__":
	main()
