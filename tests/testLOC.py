from formats import locDat

sdLoc = locDat('/home/giuseppe/Scrivania/sysmenu/loc.dat')

print '%s' % sdLoc

#concorsiMii = sdLoc.getTitle(0, 0, 0)
sdLoc.delTitle(0, 0, 0)

