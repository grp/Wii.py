from savedata import *

save = Savegame('/home/giuseppe/Scrivania/data' + str(4) + '.bin')
save.analyzeHeader()
print '%s' % save
save.getBanner()
for i in range(save.getIconsCount()):
	save.getIcon(i)
save.extractFiles()
