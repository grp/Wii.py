#!/usr/bin/python

from common import *

class SoundFile:
	def __init__(self, signal, filename, samplerate=32000):
		self.actual_file = StringIO()
		self.file = wave.open(filename, 'wb')
		self.signal = signal
		self.sr = samplerate
	def write(self):
		self.file.setparams((2, 2, self.sr, self.sr*4, 'NONE', 'noncompressed'))
		self.file.writeframes(self.signal)
		self.actual_file.seek(0)
		self.file.close()

class BNS_data(object):
	def __init__(self):
		self.magic = "DATA"
		self.size = 0x0004d000
	def eat(self, buffer, offset):
		self.magic, self.size = struct.unpack('>4sI', buffer[offset:offset+8])
		return offset + 8
	def show(self):
		print "Magic: %s" % self.magic
		print "Length: %08x" % self.size
		return
	def write(self, file):
		file.write(self.magic)
		file.write(struct.pack('>I', self.size))
		file.write(self.data)
		return

class BNS_info(object):
	def __init__(self):
		self.magic = "INFO"
		self.size = 0x000000a0
		self.codec = 0x00
		self.has_loop = 0x00
		self.chan_cnt = 0x02
		self.zero = 0x00
		self.samplerate = 0xac44
		self.pad0 = 0x0000
		self.loop_start = 0x00000000
		#sample count#
		self.loop_end = 0x00000000
		self.offset_to_chan_starts = 0x00000018
		self.pad2 = 0x00000000
		self.channel1_start_offset = 0x00000020
		self.channel2_start_offset = 0x0000002C
		self.chan1_start = 0x00000000
		self.coefficients1_offset = 0x0000038
		self.pad1 = 0x00000000
		self.chan2_start = 0x00000000
		self.coefficients2_offset = 0x00000068
		self.pad3 = 0x00000000
		self.coefficients1 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
		self.chan1_gain = 0x0000
		self.chan1_predictive_scale = 0x0000
		self.chan1_previous_value = 0x0000
		self.chan1_next_previous_value = 0x0000
		self.chan1_loop_predictive_scale = 0x0000
		self.chan1_loop_previous_value = 0x0000
		self.chan1_loop_next_previous_value = 0x0000
		self.chan1_loop_padding = 0x0000
		self.coefficients2 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
		self.chan2_gain = 0x0000
		self.chan2_predictive_scale = 0x0000
		self.chan2_previous_value = 0x0000
		self.chan2_next_previous_value = 0x0000
		self.chan2_loop_predictive_scale = 0x0000
		self.chan2_loop_previous_value = 0x0000
		self.chan2_loop_next_previous_value = 0x0000
		self.chan2_loop_padding = 0x0000
	def eat(self, buffer, offset):
		self.magic, self.size = struct.unpack('>4sI', buffer[offset+0:offset+8])
		self.codec, self.has_loop = struct.unpack('>BB', buffer[offset+8:offset+10])
		self.chan_cnt, self.zero = struct.unpack('>BB', buffer[offset+10:offset+12])
		self.samplerate, self.pad0 = struct.unpack('>HH', buffer[offset+12:offset+16])
		assert self.samplerate <= 48000
		assert self.samplerate > 32000
		self.loop_start, self.loop_end = struct.unpack('>II', buffer[offset+16:offset+24])
		co = offset + 24
		self.offset_to_chan_starts = Struct.uint32(buffer[co:co+4], endian='>')
		co += 4
		self.pad2 = Struct.uint32(buffer[co:co+4], endian='>')
		co += 4
		self.channel1_start_offset = Struct.uint32(buffer[co:co+4], endian='>')
		co += 4
		self.channel2_start_offset = Struct.uint32(buffer[co:co+4], endian='>')
		co += 4
		self.chan1_start = Struct.uint32(buffer[co:co+4], endian='>')
		co += 4
		self.coefficients1_offset = Struct.uint32(buffer[co:co+4], endian='>')
		co += 4
		if self.chan_cnt == 2:
			self.pad1 = Struct.uint32(buffer[co:co+4], endian='>')
			co += 4
			self.chan2_start = Struct.uint32(buffer[co:co+4], endian='>')
			co += 4
			self.coefficients2_offset = Struct.uint32(buffer[co:co+4], endian='>')
			co += 4
			self.pad3 = Struct.uint32(buffer[co:co+4], endian='>')
			co += 4
			for x in xrange(16):
				self.coefficients1[x] = Struct.int16(buffer[co:co+2], endian='>')
				co += 2
			self.chan1_gain = Struct.uint16(buffer[co:co+2], endian='>')
			co += 2
			self.chan1_predictive_scale = Struct.uint16(buffer[co:co+2], endian='>')
			co += 2
			self.chan1_previous_value = Struct.uint16(buffer[co:co+2], endian='>')
			co += 2
			self.chan1_next_previous_value = Struct.uint16(buffer[co:co+2], endian='>')
			co += 2
			self.chan1_loop_predictive_scale = Struct.uint16(buffer[co:co+2], endian='>')
			co += 2
			self.chan1_loop_previous_value = Struct.uint16(buffer[co:co+2], endian='>')
			co += 2
			self.chan1_loop_next_previous_value = Struct.uint16(buffer[co:co+2], endian='>')
			co += 2
			self.chan1_loop_padding = Struct.uint16(buffer[co:co+2], endian='>')
			co += 2
			for x in xrange(16):
				self.coefficients2[x] = Struct.int16(buffer[co:co+2], endian='>')
				co += 2
			self.chan2_gain = Struct.uint16(buffer[co:co+2], endian='>')
			co += 2
			self.chan2_predictive_scale = Struct.uint16(buffer[co:co+2], endian='>')
			co += 2
			self.chan2_previous_value = Struct.uint16(buffer[co:co+2], endian='>')
			co += 2
			self.chan2_next_previous_value = Struct.uint16(buffer[co:co+2], endian='>')
			co += 2
			self.chan2_loop_predictive_scale = Struct.uint16(buffer[co:co+2], endian='>')
			co += 2
			self.chan2_loop_previous_value = Struct.uint16(buffer[co:co+2], endian='>')
			co += 2
			self.chan2_loop_next_previous_value = Struct.uint16(buffer[co:co+2], endian='>')
			co += 2
			self.chan2_loop_padding = Struct.uint16(buffer[co:co+2], endian='>')
			co += 2
		elif self.chan_cnt == 1:
			for x in xrange(16):
				self.coefficients1[x] = Struct.int16(buffer[co:co+2], endian='>')
				co += 2
			self.chan1_gain = Struct.uint16(buffer[co:co+2], endian='>')
			co += 2
			self.chan1_predictive_scale = Struct.uint16(buffer[co:co+2], endian='>')
			co += 2
			self.chan1_previous_value = Struct.uint16(buffer[co:co+2], endian='>')
			co += 2
			self.chan1_next_previous_value = Struct.uint16(buffer[co:co+2], endian='>')
			co += 2
			self.chan1_loop_predictive_scale = Struct.uint16(buffer[co:co+2], endian='>')
			co += 2
			self.chan1_loop_previous_value = Struct.uint16(buffer[co:co+2], endian='>')
			co += 2
			self.chan1_loop_next_previous_value = Struct.uint16(buffer[co:co+2], endian='>')
			co += 2
			self.chan1_loop_padding = Struct.uint16(buffer[co:co+2], endian='>')
			co += 2
		return co
	def show(self):
		print "Magic: %s" % self.magic
		print "Length: %08x" % self.size
		print "Codec: %02x " % self.codec,
		if self.codec == 0: print "ADPCM"
		else: print "Unknown (Maybe >_>, please contact megazig)"
		print "Loop Flag: %02x " % self.has_loop,
		if self.has_loop == 0: print "One shot"
		else: print "Looping"
		print "Channel Count: %02x" % self.chan_cnt
		print "Zero: %02x" % self.zero
		print "Samplerate: %04x %d" % ( self.samplerate , self.samplerate )
		print "Padding: %04x" % self.pad0
		print "Loop Start: %08x" % self.loop_start
		print "Loop End: %08x" % self.loop_end
		print "Channels Starts Offsets: %08x" % self.offset_to_chan_starts
		print "Padding: %08x" % self.pad2
		print "Channel 1 Start Offset: %08x" % self.channel1_start_offset
		print "Channel 2 Start Offset: %08x" % self.channel2_start_offset
		print "Channel 1 Start: %08x" % self.chan1_start
		print "Coefficients 1 Offset: %08x" % self.coefficients1_offset
		if self.chan_cnt == 2:
			print "Padding: %08x" % self.pad1
			print "Channel 2 Start: %08x" % self.chan2_start
			print "Coefficients 2 Offset: %08x" % self.coefficients2_offset
			print "Padding: %08x" % self.pad3
			for x in xrange(16):
				print "\t\tCoefficients 1: %2d - %04x - %d" % ( x , self.coefficients1[x], self.coefficients1[x] )
			print "\tGain: %04x" % self.chan1_gain
			print "\tPredictive Scale: %04x" % self.chan1_predictive_scale
			print "\tPrevious Value: %04x" % self.chan1_previous_value
			print "\tNext Previous Value: %04x" % self.chan1_next_previous_value
			print "\tLoop Predictive Scale: %04x" % self.chan1_loop_predictive_scale
			print "\tLoop Previous Value: %04x" % self.chan1_loop_previous_value
			print "\tLoop Next Previous Value: %04x" % self.chan1_loop_next_previous_value
			print "\tPadding: %04x" % self.chan1_loop_padding
			for x in xrange(16):
				print "\t\tCoefficients 2: %2d - %04x - %d" % ( x , self.coefficients2[x], self.coefficients2[x] )
			print "\tGain: %04x" % self.chan2_gain
			print "\tPredictive Scale: %04x" % self.chan2_predictive_scale
			print "\tPrevious Value: %04x" % self.chan2_previous_value
			print "\tNext Previous Value: %04x" % self.chan2_next_previous_value
			print "\tLoop Predictive Scale: %04x" % self.chan2_loop_predictive_scale
			print "\tLoop Previous Value: %04x" % self.chan2_loop_previous_value
			print "\tLoop Next Previous Value: %04x" % self.chan2_loop_next_previous_value
			print "\tPadding: %04x" % self.chan2_loop_padding
		elif self.chan_cnt == 1:
			for x in xrange(16):
				print "\t\tCoefficients 1: %2d - %04x - %d" % ( x , self.coefficients1[x], self.coefficients1[x] )
			print "\tGain: %04x" % self.chan1_gain
			print "\tPredictive Scale: %04x" % self.chan1_predictive_scale
			print "\tPrevious Value: %04x" % self.chan1_previous_value
			print "\tNext Previous Value: %04x" % self.chan1_next_previous_value
			print "\tLoop Predictive Scale: %04x" % self.chan1_loop_predictive_scale
			print "\tLoop Previous Value: %04x" % self.chan1_loop_previous_value
			print "\tLoop Next Previous Value: %04x" % self.chan1_loop_next_previous_value
			print "\tPadding: %04x" % self.chan1_loop_padding
		return
	def write(self, file):
		file.write(self.magic)
		file.write(struct.pack('>I', self.size))
		file.write(struct.pack('>B', self.codec))
		file.write(struct.pack('>B', self.has_loop))
		file.write(struct.pack('>B', self.chan_cnt))
		file.write(struct.pack('>B', self.zero))
		file.write(struct.pack('>H', self.samplerate))
		file.write(struct.pack('>H', self.pad0))
		file.write(struct.pack('>I', self.loop_start))
		file.write(struct.pack('>I', self.loop_end))
		file.write(struct.pack('>I', self.offset_to_chan_starts))
		file.write(struct.pack('>I', self.pad2))
		file.write(struct.pack('>I', self.channel1_start_offset))
		file.write(struct.pack('>I', self.channel2_start_offset))
		file.write(struct.pack('>I', self.chan1_start))
		file.write(struct.pack('>I', self.coefficients1_offset))
		if self.chan_cnt == 2:
			file.write(struct.pack('>I', self.pad1))
			file.write(struct.pack('>I', self.chan2_start))
			file.write(struct.pack('>I', self.coefficients2_offset))
			file.write(struct.pack('>I', self.pad3))
			for x in xrange(16):
				file.write(struct.pack('>h', self.coefficients1[x]))
			file.write(struct.pack('>H', self.chan1_gain))
			file.write(struct.pack('>H', self.chan1_predictive_scale))
			file.write(struct.pack('>H', self.chan1_previous_value))
			file.write(struct.pack('>H', self.chan1_next_previous_value))
			file.write(struct.pack('>H', self.chan1_loop_predictive_scale))
			file.write(struct.pack('>H', self.chan1_loop_previous_value))
			file.write(struct.pack('>H', self.chan1_loop_next_previous_value))
			file.write(struct.pack('>H', self.chan1_loop_padding))
			for x in xrange(16):
				file.write(struct.pack('>h', self.coefficients2[x]))
			file.write(struct.pack('>H', self.chan2_gain))
			file.write(struct.pack('>H', self.chan2_predictive_scale))
			file.write(struct.pack('>H', self.chan2_previous_value))
			file.write(struct.pack('>H', self.chan2_next_previous_value))
			file.write(struct.pack('>H', self.chan2_loop_predictive_scale))
			file.write(struct.pack('>H', self.chan2_loop_previous_value))
			file.write(struct.pack('>H', self.chan2_loop_next_previous_value))
			file.write(struct.pack('>H', self.chan2_loop_padding))
		elif self.chan_cnt == 1:
			for x in xrange(16):
				file.write(struct.pack('>h', self.coefficients1[x]))
			file.write(struct.pack('>H', self.chan1_gain))
			file.write(struct.pack('>H', self.chan1_predictive_scale))
			file.write(struct.pack('>H', self.chan1_previous_value))
			file.write(struct.pack('>H', self.chan1_next_previous_value))
			file.write(struct.pack('>H', self.chan1_loop_predictive_scale))
			file.write(struct.pack('>H', self.chan1_loop_previous_value))
			file.write(struct.pack('>H', self.chan1_loop_next_previous_value))
			file.write(struct.pack('>H', self.chan1_loop_padding))
		return


class BNS_header(object):
	def __init__(self):
		self.magic = "BNS "
		self.flags = 0xfeff0100
		self.filesize = 0x0004d0c0
		self.size = 0x0020
		self.chunk_cnt = 0x0002
		self.info_off = 0x00000020
		self.info_len = 0x000000a0
		self.data_off = 0x000000c0
		self.data_len = 0x0004d000
	def eat(self, buffer, offset):
		if struct.unpack('>4s', buffer[offset:offset+4])[0] != "BNS ":
			offset += 0x20
		self.magic, self.flags  = struct.unpack('>4sI', buffer[offset+0:offset+8])
		self.filesize, self.size, self.chunk_cnt = struct.unpack('>IHH', buffer[offset+8:offset+16])
		self.info_off, self.info_len = struct.unpack('>II', buffer[offset+16:offset+24])
		self.data_off, self.data_len = struct.unpack('>II', buffer[offset+24:offset+32])
		assert self.magic == "BNS "
		assert self.info_off < self.filesize
		assert self.data_off < self.filesize
		return offset + 32
	def show(self):
		print "Magic: %s" % self.magic
		print "Flags: %08x" % self.flags
		print "Length: %08x" % self.filesize
		print "Header Size: %04x" % self.size
		print "Chunk Count: %04x" % self.chunk_cnt
		print "Info Offset: %08x" % self.info_off
		print "Info Length: %08x" % self.info_len
		print "Data Offset: %08x" % self.data_off
		print "Data Length: %08x" % self.data_len
		return
	def write(self, file):
		file.write(self.magic)
		file.write(struct.pack('>I', self.flags))
		file.write(struct.pack('>I', self.filesize))
		file.write(struct.pack('>H', self.size))
		file.write(struct.pack('>H', self.chunk_cnt))
		file.write(struct.pack('>I', self.info_off))
		file.write(struct.pack('>I', self.info_len))
		file.write(struct.pack('>I', self.data_off))
		file.write(struct.pack('>I', self.data_len))
		return

class BNS(object):
	def __init__(self):
		self.header = BNS_header()
		self.info = BNS_info()
		self.data = BNS_data()
		self.buffered_data = ""
		self.lsamps = [ [ 0 , 0 ] , [ 0 , 0 ] ]
		self.rlsamps = [ [ 0 , 0 ] , [ 0 , 0 ] ]
		self.tlsamps = [ 0 , 0 ]
		self.hbc_deftbl = [ 674 , 1040,
				3598, -1738, 
				2270, -583, 
				3967, -1969, 
				1516, 381, 
				3453, -1468, 
				2606, -617, 
				3795, -1759 ]
		self.deftbl = [ 1820 , -856 ,
				3238 , -1514 ,
				2333 , -550 ,
				3336 , -1376 ,
				2444 , -949 ,
				3666 , -1764 ,
				2654 , -701 ,
				3420 , -1398 ]
		self.phist1 = [ 0 , 0 ]
		self.phist2 = [ 0 , 0 ]
		self.errors = 0
	def find_exp(self, residual):
		exp = 0
		while residual>7.5 or residual<-8.5:
			exp += 1
			residual /= 2.0
		return exp
	def determine_std_exponent(self, idx, table, index, inbuf):
		elsamps = [ 0 , 0 ]
		max_res = 0
		factor1 = table[2*index+0]
		factor2 = table[2*index+1]
		for x in xrange(2):
			elsamps[x] = self.rlsamps[idx][x]
		for i in xrange(14):
			predictor = (elsamps[1]*factor1 + elsamps[0]*factor2) >> 11
			residual = inbuf[i] - predictor
			if residual>max_res:
				max_res = residual
			elsamps[0] = elsamps[1]
			elsamps[1] = inbuf[i]
		return self.find_exp(max_res)
	def compress_adpcm(self, idx, table, tblidx, inbuf):
		data = [0 for i in range(8)]
		error = 0
		factor1 = table[2*tblidx+0]
		factor2 = table[2*tblidx+1]
		exp = self.determine_std_exponent(idx, table, tblidx, inbuf)
		while exp<=15:
			error = 0
			data[0] = exp | (tblidx << 4)
			for x in xrange(2):
				self.tlsamps[x] = self.rlsamps[idx][x]
			j = 0
			for i in xrange(14):
				predictor = (self.tlsamps[1]*factor1 + self.tlsamps[0]*factor2) >> 11
				residual = inbuf[i] - predictor
				residual = residual >> exp
				if residual>7 or residual<-8:
					exp += 1
					break
				nibble = clamp(residual, -8, 7)
				if i&1:
					data[i/2+1] = data[i/2+1] | (nibble & 0xf)
				else:
					data[i/2+1] = nibble << 4
				predictor = predictor + (nibble << exp)
				self.tlsamps[0] = self.tlsamps[1]
				self.tlsamps[1] = clamp(predictor, -32768, 32767)
				error = error + ((self.tlsamps[1] - inbuf[i]) ** 2)
			else:
				j = 14
			if j == 14:
				break
		return error, data
	def repack_adpcm(self, idx, table, inbuf):
		data = [0 for i in range(8)]
		blsamps = [ 0 , 0 ]
		bestidx = -1
		besterror = 999999999.0
		for tblidx in xrange(8):
			error, testdata = self.compress_adpcm(idx, table, tblidx, inbuf)
			if error < besterror:
				besterror = error
				for x in xrange(8):
					data[x] = testdata[x]
				for x in xrange(2):
					blsamps[x] = self.tlsamps[x]
				bestidx = tblidx
		for x in xrange(2):
			self.rlsamps[idx][x] = blsamps[x]
		return data
	def encode(self, buffer, offset=0):
		sampsbuf = [0 for i in range(14)]
		templen = len(buffer)
		templen = templen / 4
		modlen = templen % 14
		for x in xrange(14-modlen):
			buffer = buffer + '\x00'
			buffer = buffer + '\x00'
			buffer = buffer + '\x00'
			buffer = buffer + '\x00'
		num_samps = len(buffer) / 4
		blocks = (num_samps + 13) / 14
		snddatal = []
		snddatar = []
		co = offset
		temp = 0
		for x in xrange(num_samps):
			snddatal.append(Struct.int16(buffer[co:co+2]))
			co += 2
			snddatar.append(Struct.int16(buffer[co:co+2]))
			co += 2
		data = [0 for i in range(blocks*16)]
		data1_off = 0
		data2_off = blocks * 8
		self.info.chan2_start = data2_off
		for i in xrange(blocks):
			for j in xrange(14):
				sampsbuf[j] = snddatal[i*14+j]
			out_buf = self.repack_adpcm(0, self.deftbl, sampsbuf)
			for k in xrange(8):
				data[data1_off+k] = out_buf[k]
			for j in xrange(14):
				sampsbuf[j] = snddatar[i*14+j]
			out_buf = self.repack_adpcm(1, self.deftbl, sampsbuf)
			for k in xrange(8):
				data[data2_off+k] = out_buf[k]
			data1_off += 8
			data2_off += 8
		self.info.loop_end = blocks * 7
		return data
	def create_bns(self, inbuf, samplerate=44100, channels=2):
		self.info.chan_cnt = channels
		self.info.samplerate = samplerate
		assert samplerate >=32000
		self.data.data = ''.join(Struct.int8(p) for p in self.encode(inbuf))
		self.data.size = len(self.data.data)
		self.header.data_len = self.data.size
		self.header.filesize = self.info.size + self.data.size + 8 + self.header.size
		self.info.loop_end = self.data.size - (self.data.size / 7)
		for x in xrange(16):
			self.info.coefficients1[x] = self.deftbl[x]
		if self.info.chan_cnt == 2:
			for x in xrange(16): self.info.coefficients2[x] = self.deftbl[x]
		return
	def decode_adpcm(self, index, coefs, buffer):
		outbuf = [0 for i in range(14)]
		header = Struct.uint8(buffer[0:1], endian='>')
		coef_index = (header >> 4) & 0x7
		scale = 1 << (header & 0xf)
		hist1 = self.phist1[index]
		hist2 = self.phist2[index]
		coef1 = coefs[coef_index * 2 + 0]
		coef2 = coefs[coef_index * 2 + 1]
		for x in xrange(14):
			sample_byte = Struct.uint8(buffer[x/2+1:x/2+2], endian='>')
			if x&1:
				nibble = (sample_byte & 0xf0) >> 4
			else:
				nibble = (sample_byte & 0x0f) >> 0
			if nibble >= 8:
				nibble -= 16
			sample_delta_11 = (scale * nibble) << 11
			predicted_sample_11 = coef1*hist1 + coef2*hist2
			sample_11 = predicted_sample_11 + sample_delta_11
			sample_raw = (sample_11 + 1024) >> 11
			sample_raw = clamp(sample_raw, -32768, 32767)
			outbuf[x] = sample_raw
			hist2 = hist1
			hist1 = outbuf[x]
		self.phist1[index] = hist1
		self.phist2[index] = hist2
		return outbuf
	def decode(self, buffer, offset):
		decoded_buffer = []
		if self.info.chan_cnt == 2:
			multi = 16
			coeff0 = self.info.coefficients1
			coeff1 = self.info.coefficients2
		elif self.info.chan_cnt == 1:
			multi = 8
			coeff0 = self.info.coefficients1
			coeff1 = self.info.coefficients1
		blocks = self.data.size / multi
		data1_offset = offset
		data2_offset = offset + blocks * 8
		decoded_buffer_l = [0 for i in range(blocks * 14)]
		decoded_buffer_r = [0 for i in range(blocks * 14)]
		for x in xrange(blocks):
			out_buffer = self.decode_adpcm(0, coeff0, buffer[data1_offset:data1_offset+8])
			for y in xrange(14):
				decoded_buffer_l[x*14+y] = out_buffer[y]
			out_buffer = self.decode_adpcm(1, coeff1, buffer[data2_offset:data2_offset+8])
			for y in xrange(14):
				decoded_buffer_r[x*14+y] = out_buffer[y]
			data1_offset += 8
			data2_offset += 8
		for x in xrange(blocks * 14):
			decoded_buffer.append(decoded_buffer_l[x])
			decoded_buffer.append(decoded_buffer_r[x])
		return decoded_buffer
	def eat(self, buffer, offset, decode=False):
		co = self.header.eat(buffer, offset)
		co = self.info.eat(buffer, co)
		co = self.data.eat(buffer, co)
		self.data.data = buffer[co:]
		if decode == True:
			buffer_out = self.decode(buffer, co)
			return buffer_out
		return
	def show(self):
		self.header.show()
		self.info.show()
		self.data.show()
		return
	def write(self, filename):
		file = open(filename, 'wb')
		if file:
			self.header.write(file)
			self.info.write(file)
			self.data.write(file)
			file.close()
		else:
			print "Could not open file for writing"
		return

def main():
	if sys.argv[1] == "-d":
		file = open(sys.argv[2], 'rb')
		if file:
			buffer = file.read()
			file.close()
		else:
			print "Could not open file"
			sys.exit(2)
		bns = BNS()
		wavbuffer =  bns.eat(buffer, 0x00, True)
		wavstring = ''.join(Struct.int16(p) for p in wavbuffer)
		f = SoundFile(wavstring, sys.argv[3], bns.info.samplerate)
		f.write()

	elif sys.argv[1] == "-e":
		f = wave.open(sys.argv[2], 'rb')
		num_chans = f.getnchannels()
		samplerate = f.getframerate()
		assert samplerate >= 32000
		assert samplerate <= 48000
		buffer = f.readframes(f.getnframes())
		f.close()

		bns = BNS()
		bns.create_bns(buffer, samplerate, num_chans)
		bns.write(sys.argv[3])
	elif sys.argv[1] == "-s":
		file = open(sys.argv[2], 'rb')
		if file:
			buffer = file.read()
			file.close()
		else:
			print "Could not open file"
			sys.exit(2)
		bns = BNS()
		bns.eat(buffer, 0x00, False)
		bns.show()
	else:
		print "Unknown second argument. possiblities are -d and -e"
		print "Usage: python bns.py -d <sound.bin> <output.wav>"
		print "                   == OR ==                  "
		print "       python bns.py -e <input.wav> <sound.bin> "
		print "                   == OR ==                  "
		print "       python bns.py -s <sound.bin> "
		sys.exit(1)

if __name__ == "__main__":
	# Import Psyco if available
	try:
		import psyco
		psyco.full()
	except ImportError:
		print "no psycho import"
	if len(sys.argv) == 1:
		print "Usage: python bns.py -d <sound.bin> <output.wav>"
		print "                   == OR ==                  "
		print "       python bns.py -e <input.wav> <sound.bin> "
		print "                   == OR ==                  "
		print "       python bns.py -s <sound.bin> "
		sys.exit(1)
	main()

