from Struct import *
from pyglet import clock, window, image
from pyglet.gl import *
import cStringIO
import math

from time import time


class THP():
	class THPHeader(Struct):
		__endian__ = Struct.BE
		def __format__(self):
			self.magic = Struct.string(4)
			self.version = Struct.uint32
			self.bufSize = Struct.uint32
			self.audioMaxSamples = Struct.uint32
			self.frameRate = Struct.float
			self.numFrames = Struct.uint32
			self.firstFrameSize = Struct.uint32
			self.movieDataSize = Struct.uint32
			self.compInfoDataOffsets = Struct.uint32
			self.offsetDataOffsets = Struct.uint32 #Offset to a offset table, containing offsets to each frame, this allows for starting playback from any frame. If this is 0 then it does not exist.
			self.movieDataOffsets = Struct.uint32
			self.finalFrameDataOffsets = Struct.uint32
		def __str__(self):
			ret = "\n"
			ret += "Magic: %s\n" % self.magic
			ret += "Version: %d.%d.%d\n" % (((self.version & 0xFFFF0000) >> 16), ((self.version & 0xFF00) >> 8), ((self.version & 0xFF)))
			ret += "bufSize: %s\n" % self.bufSize
			ret += "audioMaxSamples: %d\n" % self.audioMaxSamples
			ret += "frameRate: %f\n" % self.frameRate
			ret += "numFrames: %d\n" % self.numFrames
			ret += "firstFrameSize: %d\n" % self.firstFrameSize
			ret += "movieDataSize: %d\n" % self.movieDataSize
			ret += "compInfoDataOffsets: 0x%08X\n" % self.compInfoDataOffsets
			ret += "offsetDataOffsets: 0x%08X\n" % self.offsetDataOffsets
			ret += "movieDataOffsets: 0x%08X\n" % self.movieDataOffsets
			ret += "finalFrameDataOffsets: 0x%08X\n" % self.finalFrameDataOffsets
			return ret
	class THPFrameCompInfo(Struct):
		__endian__ = Struct.BE
		def __format__(self):
			self.numComponents = Struct.uint32
			self.frameComp = Struct.uint8[16]	
		def __str__(self):
			ret = ""
			ret += "Number of Components: %d\n" % self.numComponents
			return ret
	class THPCompVideoInfo(Struct):
		__endian__ = Struct.BE
		def __format__(self):
			self.width = Struct.uint32
			self.height = Struct.uint32
			self.videoType = Struct.uint32
		def __str__(self):
			tempType = ("Non-Interlaced", "Interlaced", "Odd Interlace", "3", "Even Interlace")
			ret = ""
			ret += "Width: %d\n" % self.width
			ret += "Height: %d\n" % self.height
			ret += "VideoType: %s\n" % tempType[self.videoType]
			return ret
	class THPCompAudioInfo(Struct):
		__endian__ = Struct.BE
		def __format__(self):
			self.sndChannels = Struct.uint32
			self.sndFrequency = Struct.uint32
			self.sndNumberSamples = Struct.uint32
			self.sndNumberTracks = Struct.uint32
		def __str__(self):
			ret = ""
			ret += "Channels: %d\n" % self.sndChannels
			ret += "Frequency: %d\n" % self.sndFrequency
			ret += "Samples: %d\n" % self.sndNumberSamples
			ret += "Tracks: %d\n" % self.sndNumberTracks
			return ret
	class THPFrameHeader(Struct):
		__endian__ = Struct.BE
		def __format__(self):
			self.frameSizeNext = Struct.uint32
			self.frameSizePrev = Struct.uint32
			self.vidFileSize = Struct.uint32
			self.sndFileSize = Struct.uint32
		def __str__(self):
			ret = ""
			ret += "next Frame Size: %d\n" % self.frameSizeNext
			ret += "previous Frame Size: %d\n" % self.frameSizePrev
			ret += "Video frame data size: %d\n" % self.vidFileSize
			ret += "Track file size: %d\n" % self.sndFileSize
			return ret
		def readData(self, fp, i=0):
			self.frameImage = fp.read(self.vidFileSize)
			#fileName = "frame%06d.jpg" % i
			#open("out/" + fileName, 'w+b').write(self.frameImage)
			#print "Frame: %d" % i
			startTime = time()
			start = self.frameImage.find('\xff\xda')
			end = self.frameImage.rfind('\xff\xd9')
			#print "find(%d): This took "%i, time()-startTime,start,end
			startTime = time()
			startStr = self.frameImage[:start+2]
			endStr = self.frameImage[end:]
			#print "extr(%d): This took "%i, time()-startTime
			self.frameImage = self.frameImage[start+2:end]
			self.frameImage = startStr + self.frameImage.replace('\xff','\xff\x00') + endStr
			#print self.frameImage
			
			
			return cStringIO.StringIO(self.frameImage)
	def __init__(self, movieFile=None):
		if(movieFile==None):
			print "Usage: python thp.py filename.thp"
			exit(-1)
		fp = file(movieFile, 'rb')
		HEADER = self.THPHeader()
		HEADER.unpack(fp.read(len(HEADER)))
		print HEADER
		fp.seek(HEADER.compInfoDataOffsets)
		CompInfo = self.THPFrameCompInfo()
		CompInfo.unpack(fp.read(len(CompInfo)))
		print CompInfo
		for i in range(0, CompInfo.numComponents):
			if(CompInfo.frameComp[i] == 0):
				VideoInfo = self.THPCompVideoInfo()
				VideoInfo.unpack(fp.read(len(VideoInfo)))
				print VideoInfo
			if(CompInfo.frameComp[i] == 1):
				AudioInfo = self.THPCompAudioInfo()
				AudioInfo.unpack(fp.read(len(AudioInfo)))
				print AudioInfo
				
		clock.set_fps_limit(HEADER.frameRate)
		currOff = HEADER.movieDataOffsets
		currSize = HEADER.firstFrameSize
		fp.seek(currOff)
		
		win = window.Window(VideoInfo.width, VideoInfo.height)
		fps_display = clock.ClockDisplay()
		i = 1
		j = 1
		image_index = 0
		image_period = 1.0 / HEADER.frameRate             # Reciprocal of the frame rate
		remained = 0

		while not win.has_exit:
			
			win.dispatch_events()
			win.clear()
			
			dt = clock.tick()
			
			skip = math.floor((dt+remained)/image_period)
			j += skip
			print skip, ":break:", i, j, skip
			remained = dt - skip * image_period
			
			tempFrame = self.THPFrameHeader()
			tempFrame.unpack(fp.read(len(tempFrame)))
			
			for xx in range(1,skip):
				currOff = currOff+currSize
				currSize = tempFrame.frameSizeNext
				fp.seek(currOff)
				tempFrame = self.THPFrameHeader()
				tempFrame.unpack(fp.read(len(tempFrame)))
			
			imagedat = tempFrame.readData(fp, i)
			
			pic = image.load("image.jpg",imagedat)
			pic.blit(0,0)
			
			currOff = currOff+currSize
			currSize = tempFrame.frameSizeNext
			fp.seek(currOff)
			
			
			fps_display.draw()
			win.flip()
			i += 1
		
if __name__=='__main__':
	THP(*sys.argv[1:])