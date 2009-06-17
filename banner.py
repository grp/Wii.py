#!/usr/bin/python

import sys, struct, re, hashlib, os

''' STOLEN FROM COMEX '''
def nullterm(str_plus):
    z = str_plus.find('\0')
    if z != -1:
        return str_plus[:z]
    else:
        return str_plus
        
def unnullterm(var, size):
    if len(var) > size:
        raise Exception('unnullterm: "%s" too long' % var)
    return var.ljust(size, '\0')

def bit_extract(num, start, end=None):
    if end is None:
        end = start
    mask = (2**(31 - start + 1) - 1) - (2**(31 - end) - 1)
    ret = (num & mask) >> (31 - end)
    
    return ret
    
def bit_place(num, start, end=None):
    # Just for sanity
    if end is None:
        end = start
    assert num <= 2**(end - start)
    return num << (31 - end)
    
def untv(name):
    #assert '\0' not in name
    lex = len(name) + 16
    lex -= lex % 16
    return name.ljust(lex, '\0')
''' END THEFT FROM COMEX '''
    
class BRLYT_Numoffs:
  def __init__(self):
    self.number = 0x00
    self.offset = 0x00
  def eat_numoffs(self, file, offset):
    self.number, self.offset = struct.unpack('>HH', file[offset:offset+4])
    return
  def show_numoffs(self):
    print "Number: %04x" % self.number
    print "Offset: %04x" % self.offset
    return
  def add(self):
    self.number = self.number + 1
    return
  def get_length(self):
    templength = 2 + 2
    return templength
  def write_to_file(self, file):
    file.write(struct.pack('>H', self.number))
    file.write(struct.pack('>H', self.offset))

class BRLYT_SignedColor:
  def __init__(self):
    self.color1 = 255
    self.color2 = 255
    self.color3 = 255
    self.color4 = 255
  def eat_signedcolor(self, file, offset):
    self.color1, self.color2, self.color3, self.color4 = struct.unpack('>hhhh', file[offset:offset+8])
    return
  def show_signedcolor(self):
    print "\tColor: %d" % self.color1
    print "\tColor: %d" % self.color2
    print "\tColor: %d" % self.color3
    print "\tColor: %d" % self.color4
    return
  def get_length(self):
    templength = 2 + 2 + 2 + 2
    return templength
  def write_to_file(self, file):
    file.write(struct.pack('>h', self.color1))
    file.write(struct.pack('>h', self.color2))
    file.write(struct.pack('>h', self.color3))
    file.write(struct.pack('>h', self.color4))
    return

class BRLYT_Color:
  def __init__(self):
    self.color1 = 0xFFFFFFFF
    self.color2 = 0xFFFFFFFF
    self.color3 = 0xFFFFFFFF
    self.color4 = 0xFFFFFFFF
  def eat_color(self, file, offset):
    self.color1, self.color2, self.color3, self.color4 = struct.unpack('>IIII', file[offset:offset+16])
    return
  def show_color(self):
    print "\tColor: %08x" % self.color1
    print "\tColor: %08x" % self.color2
    print "\tColor: %08x" % self.color3
    print "\tColor: %08x" % self.color4
    return
  def get_length(self):
    templength = 4 + 4 + 4 + 4
    return templength
  def write_to_file(self, file):
    file.write(struct.pack('>I', self.color1))
    file.write(struct.pack('>I', self.color2))
    file.write(struct.pack('>I', self.color3))
    file.write(struct.pack('>I', self.color4))
    return

class BRLYT_Coordinates:
  def __init__(self):
    self.coord1 = 0.0
    self.coord2 = 0.0
    self.coord3 = 1.0
    self.coord4 = 0.0
    self.coord5 = 0.0
    self.coord6 = 1.0
    self.coord7 = 1.0
    self.coord8 = 1.0
  def eat_coordinates(self, file, offset):
    self.coord1, self.coord2, self.coord3, self.coord4, self.coord5, self.coord6, self.coord7, self.coord8 = struct.unpack('>8f', file[offset:offset+32])
    return
  def show_coordinates(self):
    print "Coordinate: %f , %f" % ( self.coord1 , self.coord2 )
    print "Coordinate: %f , %f" % ( self.coord3 , self.coord4 )
    print "Coordinate: %f , %f" % ( self.coord5 , self.coord6 )
    print "Coordinate: %f , %f" % ( self.coord7 , self.coord8 )
    return
  def get_length(self):
    templength = 4 + 4 + 4 + 4 + 4 + 4 + 4 + 4
    return templength
  def write_to_file(self, file):
    file.write(struct.pack('>f', self.coord1))
    file.write(struct.pack('>f', self.coord2))
    file.write(struct.pack('>f', self.coord3))
    file.write(struct.pack('>f', self.coord4))
    file.write(struct.pack('>f', self.coord5))
    file.write(struct.pack('>f', self.coord6))
    file.write(struct.pack('>f', self.coord7))
    file.write(struct.pack('>f', self.coord8))
    return

class BRLYT_Uab:
  def __init__(self):
    self.byte1 = 0x01
    self.byte2 = 0x04
    self.byte3 = 0x05
    self.byte4 = 0x00
  def eat_uab(self, file, offset):
    self.byte1, self.byte2, self.byte3, self.byte4 = struct.unpack('BBBB', file[offset:offset+4])
    return
  def show_uab(self):
    print "UAb: %02x %02x %02x %02x" % ( self.byte1, self.byte2, self.byte3, self.byte4)
    return
  def get_length(self):
    templength = 1 + 1 + 1 + 1
    return templength
  def write_to_file(self, file):
    file.write(struct.pack('>B', self.byte1))
    file.write(struct.pack('>B', self.byte2))
    file.write(struct.pack('>B', self.byte3))
    file.write(struct.pack('>B', self.byte4))
    return

class BRLYT_Uaa:
  def __init__(self):
    self.byte1 = 0x77
    self.byte2 = 0x00
    self.byte3 = 0x00
    self.byte4 = 0x00
  def eat_uaa(self, file, offset):
    self.byte1, self.byte2, self.byte3, self.byte4 = struct.unpack('BBBB', file[offset:offset+4])
    return
  def show_uaa(self):
    print "UAa: %02x %02x %02x %02x" % ( self.byte1, self.byte2, self.byte3, self.byte4)
    return
  def get_length(self):
    templength = 1 + 1 + 1 + 1
    return templength
  def write_to_file(self, file):
    file.write(struct.pack('>B', self.byte1))
    file.write(struct.pack('>B', self.byte2))
    file.write(struct.pack('>B', self.byte3))
    file.write(struct.pack('>B', self.byte4))
    return

class BRLYT_Ua9:
  def __init__(self):
    self.byte01 = 0x00
    self.byte02 = 0x00
    self.byte03 = 0x00
    self.byte04 = 0x00
    self.byte05 = 0x00
    self.byte06 = 0x00
    self.byte07 = 0x00
    self.byte08 = 0x00
    self.byte09 = 0x00
    self.byte10 = 0x00
  def eat_ua9(self, file, offset):
    self.byte01, self.byte02, self.byte03, self.byte04, self.byte05, self.byte06, self.byte07, self.byte08, self.byte09, self.byte10 = struct.unpack('>10B', file[offset:offset+10])
    return
  def show_ua9(self):
    print "UA9: %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x" % ( self.byte01, self.byte02, self.byte03, self.byte04, self.byte05, self.byte06, self.byte07, self.byte08, self.byte09, self.byte10 )
    return
  def get_length(self):
    templength = 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1
    return templength
  def write_to_file(self, file):
    file.write(struct.pack('>B', self.byte01))
    file.write(struct.pack('>B', self.byte02))
    file.write(struct.pack('>B', self.byte03))
    file.write(struct.pack('>B', self.byte04))
    file.write(struct.pack('>B', self.byte05))
    file.write(struct.pack('>B', self.byte06))
    file.write(struct.pack('>B', self.byte07))
    file.write(struct.pack('>B', self.byte08))
    file.write(struct.pack('>B', self.byte09))
    file.write(struct.pack('>B', self.byte10))
    return

class BRLYT_Ua8:
  def __init__(self):
    self.byte1 = 0x01
    self.byte2 = 0x04
    self.byte3 = 0x05
    self.byte4 = 0x00
  def eat_ua8(self, file, offset):
    self.byte1, self.byte2, self.byte3, self.byte4 = struct.unpack('BBBB', file[offset:offset+4])
    return
  def show_ua8(self):
    print "UA8: %02x %02x %02x %02x" % ( self.byte1, self.byte2, self.byte3, self.byte4)
    return
  def get_length(self):
    templength = 1 + 1 + 1 + 1
    return templength
  def write_to_file(self, file):
    file.write(struct.pack('>B', self.byte1))
    file.write(struct.pack('>B', self.byte2))
    file.write(struct.pack('>B', self.byte3))
    file.write(struct.pack('>B', self.byte4))
    return

class BRLYT_Ua7:
  def __init__(self):
    self.a = 0x00000000
    self.b = 0x00000000
    self.c = 0.0
    self.d = 0.0
    self.e = 0.0
  def eat_ua7(self, file, offset):
    self.a, self.b, self.c, self.d, self.e = struct.unpack('>IIfff', file[offset:offset+20])
    return
  def show_ua7(self):
    print "UA7: %08x %08x %f %f %f" % ( self.a , self.b , self.c , self.d , self.e )
    return
  def get_length(self):
    templength = 4 + 4 + 4 + 4 + 4
    return templength
  def write_to_file(self, file):
    file.write(struct.pack('>I', self.a))
    file.write(struct.pack('>I', self.b))
    file.write(struct.pack('>f', self.c))
    file.write(struct.pack('>f', self.d))
    file.write(struct.pack('>f', self.e))
    return

class BRLYT_Ua6:
  def __init__(self):
    self.byte1 = 0x01
    self.byte2 = 0x04
    self.byte3 = 0x05
    self.byte4 = 0x00
  def eat_ua6(self, file, offset):
    self.byte1, self.byte2, self.byte3, self.byte4 = struct.unpack('BBBB', file[offset:offset+4])
    return
  def show_ua6(self):
    print "UA6: %02x %02x %02x %02x" % ( self.byte1, self.byte2, self.byte3, self.byte4)
    return
  def get_length(self):
    templength = 1 + 1 + 1 + 1
    return templength
  def write_to_file(self, file):
    file.write(struct.pack('>B', self.byte1))
    file.write(struct.pack('>B', self.byte2))
    file.write(struct.pack('>B', self.byte3))
    file.write(struct.pack('>B', self.byte4))
    return

class BRLYT_Ua5:
  def __init__(self):
    self.byte1 = 0x01
    self.byte2 = 0x04
    self.byte3 = 0x05
    self.byte4 = 0x00
  def eat_ua5(self, file, offset):
    self.byte1, self.byte2, self.byte3, self.byte4 = struct.unpack('BBBB', file[offset:offset+4])
    return
  def show_ua5(self):
    print "UA5: %02x %02x %02x %02x" % ( self.byte1, self.byte2, self.byte3, self.byte4)
    return
  def get_length(self):
    templength = 1 + 1 + 1 + 1
    return templength
  def write_to_file(self, file):
    file.write(struct.pack('>B', self.byte1))
    file.write(struct.pack('>B', self.byte2))
    file.write(struct.pack('>B', self.byte3))
    file.write(struct.pack('>B', self.byte4))
    return

class BRLYT_Ua4:
  def __init__(self):
    self.byte1 = 0x01
    self.byte2 = 0x04
    self.byte3 = 0x05
    self.byte4 = 0x00
  def eat_ua4(self, file, offset):
    self.byte1, self.byte2, self.byte3, self.byte4 = struct.unpack('BBBB', file[offset:offset+4])
    return
  def show_ua4(self):
    print "UA4: %02x %02x %02x %02x" % ( self.byte1, self.byte2, self.byte3, self.byte4)
    return
  def get_length(self):
    templength = 1 + 1 + 1 + 1
    return templength
  def write_to_file(self, file):
    file.write(struct.pack('>B', self.byte1))
    file.write(struct.pack('>B', self.byte2))
    file.write(struct.pack('>B', self.byte3))
    file.write(struct.pack('>B', self.byte4))
    return

class BRLYT_Ua3:
  def __init__(self):
    self.byte1 = 0x01
    self.byte2 = 0x04
    self.byte3 = 0x1e
    self.byte4 = 0x00
  def eat_ua3(self, file, offset):
    self.byte1, self.byte2, self.byte3, self.byte4 = struct.unpack('BBBB', file[offset:offset+4])
    return
  def show_ua3(self):
    print "UA3: %02x %02x %02x %02x" % ( self.byte1, self.byte2, self.byte3, self.byte4)
    return
  def get_length(self):
    templength = 1 + 1 + 1 + 1
    return templength
  def write_to_file(self, file):
    file.write(struct.pack('>B', self.byte1))
    file.write(struct.pack('>B', self.byte2))
    file.write(struct.pack('>B', self.byte3))
    file.write(struct.pack('>B', self.byte4))

class BRLYT_TextureMap:
  def __init__(self):
    self.x1 = 0.0
    self.y1 = 0.0
    self.angle = 0.0
    self.x2 = 1.0
    self.y2 = 1.0
  def eat_texturemap(self, file, offset):
    self.x1, self.y1, self.angle, self.x2, self.y2 = struct.unpack('>fffff', file[offset:offset+20])
    return
  def show_texturemap(self):
    print "Coordinate 1: %f %f" % ( self.x1 , self.y1 )
    print "Angle: %f" % self.angle
    print "Coordinate 2: %f %f" % ( self.x2 , self.y2 )
    return
  def get_length(self):
    templength = 4 + 4 + 4 + 4 + 4
    return templength
  def write_to_file(self, file):
    file.write(struct.pack('>f', self.x1))
    file.write(struct.pack('>f', self.y1))
    file.write(struct.pack('>f', self.angle))
    file.write(struct.pack('>f', self.x2))
    file.write(struct.pack('>f', self.y2))
    return

class BRLYT_TexRef:
  def __init__(self):
    self.texture_offset = 0x0000
    self.wrap_s = 0x00
    self.wrap_t = 0x00
  def eat_texref(self, file, offset):
    self.texture_offset, self.wrap_s, self.wrap_t = struct.unpack('>HBB', file[offset:offset+4])
    return
  def show_texref(self):
    print "Texture Offset: %04x" % self.texture_offset
    print "Wrap_S: %02x" % self.wrap_s
    print "Wrap_T: %02x" % self.wrap_t
    return
  def set_texture(self, texture, wrap_s=0, wrap_t=0):
    setl.texture_offset = texture
    self.wrap_s = wrap_s
    self.wrap_s = wrap_t
  def get_length(self):
    templength = 2 + 1 + 1
    return templength
  def write_to_file(self, file):
    file.write(struct.pack('>H', self.texture_offset))
    file.write(struct.pack('>B', self.wrap_s))
    file.write(struct.pack('>B', self.wrap_t))
    return

class BRLYT_Material:
  def __init__(self):
    self.name = "material00"
    self.forecolor = BRLYT_SignedColor()
    self.backcolor = BRLYT_SignedColor()
    self.unknowncolor = BRLYT_SignedColor()
    self.tevcolor = BRLYT_Color()
    self.flags = 0x00000000
    self.texrefs = { }
    self.texturemaps = { }
    self.ua3s = { }
    self.ua4s = { }
    self.ua5s = { }
    self.ua6s = { }
    self.ua7s = { }
    self.ua8s = { }
    self.ua9s = { }
    self.uaas = { }
    self.uabs = { }
  def eat_material(self, file, offset):
    dummy, self.name = struct.unpack('>I20s', file[offset-4:offset+20])
    self.forecolor.eat_signedcolor(file, offset+20)
    self.backcolor.eat_signedcolor(file, offset+28)
    self.unknowncolor.eat_signedcolor(file, offset+36)
    self.tevcolor.eat_color(file, offset+44)
    dummy, self.flags = struct.unpack('>II', file[offset+60-4:offset+60+4])
    file_offset = offset + 64
    for x in range(bit_extract(self.flags, 28, 31)):
      self.texrefs[x] = BRLYT_TexRef()
      self.texrefs[x].eat_texref(file, file_offset)
      file_offset = file_offset + 4
    for x in range(bit_extract(self.flags, 24, 27)):
      self.texturemaps[x] = BRLYT_TextureMap()
      self.texturemaps[x].eat_texturemap(file, file_offset)
      file_offset = file_offset + 20
    for x in range(bit_extract(self.flags, 20, 23)):
      self.ua3s[x] = BRLYT_Ua3()
      self.ua3s[x].eat_ua3(file, file_offset)
      file_offset = file_offset + 4
    for x in range(bit_extract(self.flags, 6)):
      self.ua4s[x] = BRLYT_Ua4()
      self.ua4s[x].eat_ua4(file, file_offset)
      file_offset = file_offset + 4
    for x in range(bit_extract(self.flags, 4)):
      self.ua5s[x] = BRLYT_Ua5()
      self.ua5s[x].eat_ua5(file, file_offset)
      file_offset = file_offset + 4
    for x in range(bit_extract(self.flags, 19)):
      self.ua6s[x] = BRLYT_Ua6()
      self.ua6s[x].eat_ua6(file, file_offset)
      file_offset = file_offset + 4
    for x in range(bit_extract(self.flags, 17, 18)):
      self.ua7s[x] = BRLYT_Ua7()
      self.ua7s[x].eat_ua7(file, file_offset)
      file_offset = file_offset + 4
    for x in range(bit_extract(self.flags, 14, 16)):
      self.ua8s[x] = BRLYT_Ua8()
      self.ua8s[x].eat_ua8(file, file_offset)
      file_offset = file_offset + 4
    for x in range(bit_extract(self.flags, 9, 13)):
      self.ua9s[x] = BRLYT_Ua9()
      self.ua9s[x].eat_ua9(file, file_offset)
      file_offset = file_offset + 4
    for x in range(bit_extract(self.flags, 8)):
      self.uaas[x] = BRLYT_Uaa()
      self.uaas[x].eat_uaa(file, file_offset)
      file_offset = file_offset + 4
    for x in range(bit_extract(self.flags, 7)):
      self.uabs[x] = BRLYT_Uab()
      self.uabs[x].eat_uab(file, file_offset)
      file_offset = file_offset + 4
    return
  def show_material(self):
    print "Name: %s" % self.name.rstrip('\x00')
    print "Forecolor: "
    self.forecolor.show_signedcolor()
    print "Backcolor: "
    self.backcolor.show_signedcolor()
    print "Unknown Color: "
    self.unknowncolor.show_signedcolor()
    print "Tev Color: "
    self.tevcolor.show_color()
    print "Flags: %08x" % self.flags
    for x in range(bit_extract(self.flags, 28, 31)):
      self.texrefs[x].show_texref()
    for x in range(bit_extract(self.flags, 24, 27)):
      self.texturemaps[x].show_texturemap()
    for x in range(bit_extract(self.flags, 20, 23)):
      self.ua3s[x].show_ua3()
    for x in range(bit_extract(self.flags, 6)):
      self.ua4s[x].show_ua4()
    for x in range(bit_extract(self.flags, 4)):
      self.ua5s[x].show_ua5()
    for x in range(bit_extract(self.flags, 19)):
      self.ua6s[x].show_ua6()
    for x in range(bit_extract(self.flags, 17, 18)):
      self.ua7s[x].show_ua7()
    for x in range(bit_extract(self.flags, 14, 16)):
      self.ua8s[x].show_ua8()
    for x in range(bit_extract(self.flags, 9, 13)):
      self.ua9s[x].show_ua9()
    for x in range(bit_extract(self.flags, 8)):
      self.uaas[x].show_uaa()
    for x in range(bit_extract(self.flags, 7)):
      self.uabs[x].show_uab()
    return
  def set_texture(self, texture, wrap_s=0, wrap_t=0):
    self.texrefs[0] = BRLYT_TexRef()
    self.texrefs[0].set_texture(texture, wrap_s, wrap_t)
  def get_length(self):
    templength = 20 + self.forecolor.get_length() + self.backcolor.get_length()
    templength = templength + self.unknowncolor.get_length() + self.tevcolor.get_length() + 4
    for x in range(len(self.texrefs)):
      templength = templength + self.texrefs[x].get_length()
    for x in range(len(self.texturemaps)):
      templength = templength + self.texturemaps[x].get_length()
    for x in range(len(self.ua3s)):
      templength = templength + self.ua3s[x].get_length()
    for x in range(len(self.ua4s)):
      templength = templength + self.ua4s[x].get_length()
    for x in range(len(self.ua5s)):
      templength = templength + self.ua5s[x].get_length()
    for x in range(len(self.ua6s)):
      templength = templength + self.ua6s[x].get_length()
    for x in range(len(self.ua7s)):
      templength = templength + self.ua7s[x].get_length()
    for x in range(len(self.ua8s)):
      templength = templength + self.ua8s[x].get_length()
    for x in range(len(self.ua9s)):
      templength = templength + self.ua9s[x].get_length()
    for x in range(len(self.uaas)):
      templength = templength + self.uaas[x].get_length()
    for x in range(len(self.uabs)):
      templength = templength + self.uabs[x].get_length()
    return templength
  def write_to_file(self, file):
    file.write(struct.pack('>20s', self.name))
    self.forecolor.write_to_file(file)
    self.backcolor.write_to_file(file)
    self.unknowncolor.write_to_file(file)
    self.tevcolor.write_to_file(file)
    file.write(struct.pack('>I', self.flags))
    for x in range(bit_extract(self.flags, 28, 31)):
      self.texrefs[x].write_to_file(file)
    for x in range(bit_extract(self.flags, 24, 27)):
      self.texturemaps[x].write_to_file(file)
    for x in range(bit_extract(self.flags, 20, 23)):
      self.ua3s[x].write_to_file(file)
    for x in range(bit_extract(self.flags, 6)):
      self.ua4s[x].write_to_file(file)
    for x in range(bit_extract(self.flags, 4)):
      self.ua5s[x].write_to_file(file)
    for x in range(bit_extract(self.flags, 19)):
      self.ua6s[x].write_to_file(file)
    for x in range(bit_extract(self.flags, 17, 18)):
      self.ua7s[x].write_to_file(file)
    for x in range(bit_extract(self.flags, 14, 16)):
      self.ua8s[x].write_to_file(file)
    for x in range(bit_extract(self.flags, 9, 13)):
      self.ua9s[x].write_to_file(file)
    for x in range(bit_extract(self.flags, 8)):
      self.uaas[x].write_to_file(file)
    for x in range(bit_extract(self.flags, 7)):
      self.uabs[x].write_to_file(file)
    return

class BRLYT_Pane:
  def __init__(self):
    self.orientation1 = 0x01
    self.orientation2 = 0x04
    self.alpha1 = 0xff
    self.alpha2 = 0x00
    self.name = "RootPane"
    self.x = 0.0
    self.y = 0.0
    self.z = 0.0
    self.flipx = 0.0
    self.flipy = 0.0
    self.angle = 0.0
    self.xmag = 1.0
    self.ymag = 1.0
    self.width = 608.0
    self.height = 456.0
  def eat_pane(self, file, offset):
    self.orientation1, self.orientation2, self.alpha1, self.alpha2 = struct.unpack('BBBB', file[offset:offset+4])
    self.name, self.x, self.y, self.z = struct.unpack('>24sfff', file[offset+0x04:offset+0x04+36])
    self.flipx, self.flipy, self.angle = struct.unpack('>fff', file[offset+0x28:offset+0x28+12])
    self.xmag, self.ymag = struct.unpack('>ff', file[offset+0x34:offset+0x34+8])
    self.width, self.height = struct.unpack('>ff', file[offset+0x3C:offset+0x3C+8])
    return
  def show_pane(self):
    print "Orientation: %02x %02x" % (self.orientation1 , self.orientation2)
    print "Alpha: %02x %02x" % (self.alpha1 , self.alpha2)
    print "Name: %s" % self.name.rstrip('\x00')
    print "X: %f" % self.x
    print "y: %f" % self.y
    print "z: %f" % self.z
    print "flip x: %f" % self.flipx
    print "flip y: %f" % self.flipy
    print "angle: %f" % self.angle
    print "x zoom: %f" % self.xmag
    print "y zoom: %f" % self.ymag
    print "width: %f" % self.width
    print "height: %f" % self.height
    return
  def get_length(self):
    templength = 1 + 1 + 1 + 1 + 24 + 4 + 4 + 4 + 4 + 4 + 4 + 4 + 4 + 4 + 4
    return templength
  def write_to_file(self, file):
    file.write(struct.pack('>B', self.orientation1))
    file.write(struct.pack('>B', self.orientation2))
    file.write(struct.pack('>B', self.alpha1))
    file.write(struct.pack('>B', self.alpha2))
    file.write(struct.pack('>24s', self.name))
    file.write(struct.pack('>f', self.x))
    file.write(struct.pack('>f', self.y))
    file.write(struct.pack('>f', self.z))
    file.write(struct.pack('>f', self.flipx))
    file.write(struct.pack('>f', self.flipy))
    file.write(struct.pack('>f', self.angle))
    file.write(struct.pack('>f', self.xmag))
    file.write(struct.pack('>f', self.ymag))
    file.write(struct.pack('>f', self.width))
    file.write(struct.pack('>f', self.height))
    return

class BRLYT_gre1:
  def __init__(self):
    self.magic = "gre1"
    self.length = 0x08
  def eat_tag(self, file, offset):
    self.magic, self.length = struct.unpack('>4sI', file[offset:offset+8])
    return
  def show_tag(self):
    print "Magic: %s" % self.magic
    print "Length: %08x" % self.length
    return
  def get_length(self):
    self.length = 4 + 4
    return self.length
  def write_to_file(self, file):
    file.write(self.magic)
    file.write(struct.pack('>I', self.length))
    return

class BRLYT_grs1:
  def __init__(self):
    self.magic = "grs1"
    self.length = 0x08
  def eat_tag(self, file, offset):
    self.magic, self.length = struct.unpack('>4sI', file[offset:offset+8])
    return
  def show_tag(self):
    print "Magic: %s" % self.magic
    print "Length: %08x" % self.length
    return
  def get_length(self):
    self.length = 4 + 4
    return self.length
  def write_to_file(self, file):
    file.write(self.magic)
    file.write(struct.pack('>I', self.length))
    return

class BRLYT_grp1:
  def __init__(self):
    self.magic = "grp1"
    self.length = 0x00000000
    self.name = "RootGroup"
    self.numsubs = 0x0000
    self.unknown = 0x0000
    self.subs = []
  def eat_tag(self, file, offset):
    self.magic, self.length = struct.unpack('>4sI', file[offset:offset+8])
    self.name, self.numsubs, self.unknown = struct.unpack('>16sHH', file[offset+0x08:offset+0x08+20])
    for x in range(self.numsubs):
      dummy, subname = struct.unpack('>I16s', file[offset+0x1C+16*x-4:offset+0x1C+16*x+16])
      self.subs.append(subname)
    return
  def show_tag(self):
    print "Magic: %s" % self.magic
    print "Length: %08x" % self.length
    print "Name: %s" % self.name.rstrip('\x00')
    print "Number of Subs: %04x" % self.numsubs
    print "Unknown: %04x" % self.unknown
    for x in self.subs:
      print "Sub: %s" % x.rstrip('\x00')
    return
  def get_length(self):
    self.length = 4 + 4 + 16 + 2 + 2 + self.numsubs * 16
    return self.length
  def write_to_file(self, file):
    file.write(self.magic)
    file.write(struct.pack('>I', self.length))
    file.write(struct.pack('>16s', self.name))
    file.write(struct.pack('>H', self.numsubs))
    file.write(struct.pack('>H', self.unknown))
    for x in self.subs:
      file.write(struct.pack('>16s', x))
    return

class BRLYT_txt1:
  def __init__(self):
    self.magic = "txt1"
    self.pane = BRLYT_Pane()
    len1 = 0x0000
    len2 = 0x0000
    mat_off = 0x0000
    font = 0x0000
    unknown = 0x00
    padding1 = 0
    padding2 = 0
    padding3 = 0
    name_offs = 0x00000000
    color1 = 0xFFFFFFFF
    color2 = 0x00000000
    font_size_x = 32.0
    font_size_y = 32.0
    char_space = 32.0
    line_space = 32.0
  def eat_tag(self, file, offset):
    self.magic, self.length = struct.unpack('>4sI', file[offset:offset+8])
    self.pane.eat_pane(file, offset+8)
    self.len1, self.len2, self.mat_off, self.font = struct.unpack('>HHHH', file[offset+0x08:offset+0x08+8])
    self.unknown, self.padding1, self.padding2, self.padding3 = struct.unpack('>BBBB', file[offset+0x10:offset+0x10+4])
    self.name_offs, self.color1, self.color2 = struct.unpack('>III', file[offset+0x14:offset+0x14+12])
    self.font_size_x, self.font_size_y = struct.unpack('>ff', file[offset+0x20:offset+0x20+8])
    self.char_space, self.line_space = struct.unpack('>ff', file[offset+0x28:offset+0x28+8])
    text = file[offset+0x30:offset+0x30+self.len2]
    self.text = unicode(text, 'utf_16_be').rstrip('\x00')
    return
  def show_tag(self):
    print "Magic: %s" % self.magic
    print "Length: %08x" % self.length
    self.pane.show_pane()
    print "Length: %04x %04x" % ( self.len1 , self.len2 )
    print "Material: %04x" % self.mat_off
    print "Font: %04x" % self.font
    print "Unknown: %02x" % self.unknown
    print "Padding: %02x %02x %02x" % ( self.padding1 , self.padding2 , self.padding3 )
    print "Name offset: %08x" % self.name_offs
    print "Color1: %08x" % self.color1
    print "Color2: %08x" % self.color2
    print "Font Size X: %f" % self.font_size_x
    print "Font Size Y: %f" % self.font_size_y
    print "Character Spacing: %f" % self.char_space
    print "Line Spacing: %f" % self.line_space
    print "Text: ", self.text # N E E D S   S O M E   W O R K
    return
  def get_text_length(self):
    return len(self.text)
  def get_length(self):
    templength = 4 + 4 + self.pane.get_length()
    templength = templength + 2 + 2 + 2 + 2 + 1 + 1 + 1 + 1
    templength = templength + 4 + 4 + 4 + 4 + 4 + 4 + 4
    templength =  templength + self.get_text_length()
    self.length = templength
    return self.length
  def write_to_file(self, file):
    file.write(self.magic)
    file.write(struct.pack('>I', self.length))
    self.pane.write_to_file(file)
    file.write(struct.pack('>H', self.len1))
    file.write(struct.pack('>H', self.len2))
    file.write(struct.pack('>H', self.mat_off))
    file.write(struct.pack('>H', self.font))
    file.write(struct.pack('>B', self.unknown))
    file.write(struct.pack('>B', self.padding1))
    file.write(struct.pack('>B', self.padding2))
    file.write(struct.pack('>B', self.padding3))
    file.write(struct.pack('>I', self.name_offs))
    file.write(struct.pack('>I', self.color1))
    file.write(struct.pack('>I', self.color2))
    file.write(struct.pack('>f', self.font_size_x))
    file.write(struct.pack('>f', self.font_size_y))
    file.write(struct.pack('>f', self.char_space))
    file.write(struct.pack('>f', self.line_space))
    text = untv(unicode(self.text).encode('utf_16_be'))
    file.write(text)
    return

class BRLYT_pic1:
  def __init__(self):
    self.magic = "pic1"
    self.length = 0x0000000
    self.pane = BRLYT_Pane()
    self.vtx_color1 = 0xFFFFFFFF
    self.vtx_color2 = 0xFFFFFFFF
    self.vtx_color3 = 0xFFFFFFFF
    self.vtx_color4 = 0xFFFFFFFF
    self.mat_off = 0x0000
    self.num_coordinates = 0x01
    self.padding = 0x00
    self.coordinates = { }
    self.coordinates[0] = BRLYT_Coordinates()
  def eat_tag(self, file, offset):
    self.magic, self.length = struct.unpack('>4sI', file[offset:offset+8])
    self.pane.eat_pane(file, offset+8)
    self.vtx_color1, self.vtx_color2, self.vtx_color3, self.vtx_color4 = struct.unpack('>IIII', file[offset+0x4C:offset+0x4C+16])
    self.mat_off, self.num_coordinates, self.padding = struct.unpack('>HBB', file[offset+0x5C:offset+0x5C+4])
    for x in range(self.num_coordinates):
      self.coordinates[x] = BRLYT_Coordinates()
      self.coordinates[x].eat_coordinates(file, offset+0x60+x*32)
    return
  def show_tag(self):
    print "Magic: %s" % self.magic
    print "Length: %08x" % self.length
    self.pane.show_pane()
    print "Vertex Colors: %08x %08x %08x %08x" % (self.vtx_color1, self.vtx_color2, self.vtx_color3, self.vtx_color4)
    print "Material Offset: %04x" % self.mat_off
    print "Number of Coordinates: %02x" % self.num_coordinates
    print "Padding: %02x" % self.padding
    for x in range(len(self.coordinates)):
      self.coordinates[x].show_coordinates()
    return
  def get_length(self):
    templength = 4 + 4 + self.pane.get_length()
    templength = templength + 4 + 4 + 4 + 2 + 1 + 1
    for x in range(len(self.coordinates)):
      templength = templength + self.coordinates[x].get_length()
    self.length = templength
    return self.length
  def write_to_file(self, file):
    file.write(self.magic)
    file.write(struct.pack('>I', self.length))
    self.pane.write_to_file(file)
    file.write(struct.pack('>I', self.vtx_color1))
    file.write(struct.pack('>I', self.vtx_color2))
    file.write(struct.pack('>I', self.vtx_color3))
    file.write(struct.pack('>I', self.vtx_color4))
    file.write(struct.pack('>H', self.mat_off))
    file.write(struct.pack('>B', self.num_coordinates))
    file.write(struct.pack('>B', self.padding))
    for x in range(len(self.coordinates)):
      self.coordinates[x].write_to_file(file)
    return

class BRLYT_WindowAddon3:
  def __init__(self):
    self.unknown1 = 0x0000
    self.unknown2 = 0x0000
  def eat_windowaddon3(self, file, offset):
    self.unknown1, self.unknown2 = struct.unpack('>HH', file[offset:offset+4])
    return
  def show_windowaddon3(self):
    print "Unknown: %04x %04x" % ( self.unknown1 , self.unknown2 )
    return
  def get_length(self):
    templength = 2 + 2
    return templength
  def write_to_file(self, file):
    file.write(struct.pack('>H', self.unknown1))
    file.write(struct.pack('>H', self.unknown2))
    return

class BRLYT_WindowAddon2:
  def __init__(self):
    self.unknown1 = 0x00000000
    self.unknown2 = 0x00000000
    self.unknown3 = 0x00000000
    self.unknown4 = 0x00000000
  def eat_windowaddon2(self, file, offset):
    self.unknown1, self.unknown2, self.unknown3, self.unknown4 = struct.unpack('>IIII', file[offset:offset+16])
    return
  def show_windowaddon2(self):
    print "Unknown: %08x %08x %08x %08x" % ( self.unknown1, self.unknown2, self.unknown3, self.unknown4 )
    return
  def get_length(self):
    templength = 4 + 4 + 4 + 4
    return templength
  def write_to_file(self, file):
    file.write(struct.pack('>I', self.unknown1))
    file.write(struct.pack('>I', self.unknown2))
    file.write(struct.pack('>I', self.unknown3))
    file.write(struct.pack('>I', self.unknown4))
    return

class BRLYT_WindowAddon1:
  def __init__(self):
    self.unknown1 = 0.0
    self.unknown2 = 0.0
    self.unknown3 = 0.0
    self.unknown4 = 0.0
    self.count = 0x01
    self.padding1 = 0x00
    self.padding2 = 0x00
    self.padding3 = 0x00
    self.offset1 = 0x00000068
    self.offset2 = 0x0000007C
  def eat_windowaddon1(self, file, offset):
    self.unknown1, self.unknown2, self.unknown3, self.unknown4 = struct.unpack('>ffff', file[offset:offset+16])
    self.count, self.padding1, self.padding2, self.padding3 = struct.unpack('>BBBB', file[offset+0x10:offset+0x10+4])
    self.offset1, self.offset2 = struct.unpack('>II', file[offset+0x14:offset+0x14+8])
    return
  def show_windowaddon1(self):
    print "Unknown: %f %f %f %f" % ( self.unknown1, self.unknown2, self.unknown3, self.unknown4 )
    print "Count: %02x" % self.count
    print "Padding %02x %02x %02x" % ( self.padding1, self.padding2, self.padding3 )
    print "Offset 1: %08x" % self.offset1
    print "Offset 2: %08x" % self.offset2
    return
  def get_length(self):
    templength = 4 + 4 + 4 + 4 + 1 + 1 + 1 + 1 + 4 + 4
    return templength
  def write_to_file(self, file):
    file.write(struct.pack('>B', self.count))
    file.write(struct.pack('>B', self.padding1))
    file.write(struct.pack('>B', self.padding2))
    file.write(struct.pack('>B', self.padding3))
    file.write(struct.pack('>I', self.offset1))
    file.write(struct.pack('>I', self.offset2))
    return

class BRLYT_wnd1:
  def __init__(self):
    self.magic = "wnd1"
    self.pane = BRLYT_Pane()
    self.addon1 = BRLYT_WindowAddon1()
    self.addon2 = BRLYT_WindowAddon2()
    self.addon3 = BRLYT_WindowAddon3()
    self.offsets = []
    self.materials = []
  def eat_tag(self, file, offset):
    self.magic, self.length = struct.unpack('>4sI', file[offset:offset+8])
    self.pane.eat_pane(file, offset+8)
    self.addon1.eat_windowaddon1(file, offset+0x4c)
    self.addon2.eat_windowaddon2(file, offset+0x4c+28)
    self.addon3.eat_windowaddon3(file, offset+0x4c+44)
    if self.addon1.offset1 == 0x9c:
      self.addon4 = BRLYT_Coordinates()
      self.addon4.eat_coordinates(file, offset+0x4c+48)
    for x in range(self.addon1.count):
      dummy, offs = struct.unpack('>II', file[offset+0x4c+48+32-4:offset+0x4c+48+32+4])
      self.offsets.append(offs)
    for x in range(self.addon1.count):
      dummy, mat = struct.unpack('>II', file[offset+0x4c+48+32+self.addon1.count*4-4:offset+0x4c+48+32+self.addon1.count*4+4])
      self.materials.append(mat)
      return
  def show_tag(self):
    print "Magic: %s" % self.magic
    print "Length: %08x" % self.length
    self.pane.show_pane()
    self.addon1.show_windowaddon1()
    self.addon2.show_windowaddon2()
    self.addon3.show_windowaddon3()
    if self.addon1.offset1 == 0x9c:
      self.addon4.show_coordinates()
    for x in range(self.addon1.count):
      print "Offset: %08x" % self.offsets[x]
      print "Material: %08x" % self.materials[x]
    return
  def get_length(self):
    templength = 4 + 4 + self.addon1.get_length() + self.addon2.get_length() + self.addon3.get_length()
    if self.addon1.offset1 == 0x9c:
      templength = templength + self.addon4.get_length()
    templength = templength + self.addon1.count * 8
    self.length = templength
    return self.length
  def write_to_file(self, file):
    file.write(self.magic)
    file.write(struct.pack('>I', self.length))
    self.pane.write_to_file(file)
    self.addon1.write_to_file(file)
    self.addon2.write_to_file(file)
    self.addon3.write_to_file(file)
    if self.addon1.offset1 == 0x9c:
      self.addon4.write_to_file(file)
    tempOffset = self.addon1.count * 4
    for x in range(self.addon1.count):
      file.write(struct.pack('>I', tempOffset))
      self.offsets[x] = tempOffset
    for x in self.materials:
      file.write(struct.pack('>I', x))
    return

class BRLYT_bnd1:
  def __init__(self):
    self.magic = "bnd1"
    self.pane = BRLYT_Pane()
  def eat_tag(self, file, offset):
    self.magic, self.length = struct.unpack('>4sI', file[offset:offset+8])
    self.pane.eat_pane(file, offset+8)
    return
  def show_tag(self):
    print "Magic: %s" % self.magic
    print "Length: %08x" % self.length
    self.pane.show_pane()
    return
  def get_length(self):
    self.length = 4 + 4 + self.pane.get_length()
    return self.length
  def write_to_file(self, file):
    file.write(self.magic)
    file.write(struct.pack('>I', self.length))
    self.pane.write_to_file(file)
    return

class BRLYT_pae1:
  def __init__(self):
    self.magic = "pae1"
    self.length = 0x08
  def eat_tag(self, file, offset):
    self.magic, self.length = struct.unpack('>4sI', file[offset:offset+8])
    return
  def show_tag(self):
    print "Magic: %s" % self.magic
    print "Length: %08x" % self.length
    return
  def get_length(self):
    self.length = 4 + 4
    return self.length
  def write_to_file(self, file):
    file.write(self.magic)
    file.write(struct.pack('>I', self.length))
    return

class BRLYT_pas1:
  def __init__(self):
    self.magic = "pas1"
    self.length = 0x08
  def eat_tag(self, file, offset):
    self.magic, self.length = struct.unpack('>4sI', file[offset:offset+8])
    return
  def show_tag(self):
    print "Magic: %s" % self.magic
    print "Length: %08x" % self.length
    return
  def get_length(self):
    self.length = 4 + 4
    return self.length
  def write_to_file(self, file):
    file.write(self.magic)
    file.write(struct.pack('>I', self.length))
    return

class BRLYT_pan1:
  def __init__(self):
    self.magic = "pan1"
    self.pane = BRLYT_Pane()
  def eat_tag(self, file, offset):
    self.magic, self.length = struct.unpack('>4sI', file[offset:offset+8])
    self.pane.eat_pane(file, offset+8)
    return
  def show_tag(self):
    print "Magic: %s" % self.magic
    print "Length: %08x" % self.length
    self.pane.show_pane()
    return
  def get_length(self):
    self.length = 4 + 4 + self.pane.get_length()
    return self.length
  def write_to_file(self, file):
    file.write(self.magic)
    file.write(struct.pack('>I', self.length))
    self.pane.write_to_file(file)
    return

class BRLYT_mat1:
  def __init__(self):
    self.magic = "mat1"
    self.numoffs = BRLYT_Numoffs()
    self.offsets = []
    self.materials = { }
  def eat_tag(self, file, offset):
    self.magic, self.length = struct.unpack('>4sI', file[offset:offset+8])
    self.numoffs.eat_numoffs(file, offset+8)
    for x in range(self.numoffs.number):
      dummy, offs = struct.unpack('>II', file[offset+0x0C+4*x-4:offset+0x0C+4*x+4])
      self.offsets.append(offs)
      self.materials[x] = BRLYT_Material()
      self.materials[x].eat_material(file, offset+self.offsets[x])
    return
  def show_tag(self):
    print "Magic: %s" % self.magic
    print "Length: %08x" % self.length
    self.numoffs.show_numoffs()
    for x in range(self.numoffs.number):
      print "Offsets[%d]: %08x" % ( x , self.offsets[x] )
      self.materials[x].show_material()
    return
  def add_material(self, material, texture):
    self.materials[self.numoffs.number] = BRLYT_Material()
    self.numoffs.add()
    self.materials[self.numoffs.number].name = material
    self.materials[self.numoffs.number].set_texture(texture)
  def get_length(self):
    templength = 4 + 4 + 4 + self.numoffs.number * 4
    for x in range(self.numoffs.number):
      templength = templength + self.materials[x].get_length()
    self.length = templength
    return self.length
  def write_to_file(self, file):
    file.write(self.magic)
    file.write(struct.pack('>I', self.length))
    self.numoffs.write_to_file(file)
    tempOffset = self.numoffs.number * 4
    for x in range(self.numoffs.number):
      file.write(struct.pack('>I', tempOffset))
      #self.offsets[x] = tempOffset
      tempOffset = tempOffset + self.materials[x].get_length()
    for x in range(len(self.materials)):
      self.materials[x].write_to_file(file)
    return

class BRLYT_fnl1:
  def __init__(self):
    self.magic = "fnl1"
    self.numoffs = BRLYT_Numoffs()
    self.offsets = []
    self.fonts = []
  def eat_tag(self, file, offset):
    self.magic, self.length = struct.unpack('>4sI', file[offset:offset+8])
    self.numoffs.eat_numoffs(file, offset+8)
    for x in range(self.numoffs.number):
      ''' Grab font name '''
      offs, unknown = struct.unpack('>II', file[offset+8+4+x*8:offset+8+4+x*8+8])
      self.offsets.append(offs)
      font = nullterm(file[offset+12+self.offsets[x]:])
      self.fonts.append(font)
    return
  def show_tag(self):
    print "Magic: %s" % self.magic
    print "Length: %08x" % self.length
    self.numoffs.show_numoffs()
    for x in range(len(self.fonts)):
      print "Font: %s offset: %08x" % ( self.fonts[x] , self.offsets[x] )
    return
  def add_font(self, font):
    self.fonts.append(font)
    self.numoffs.add()
    if len(self.fonts) > 1:
      self.offsets.append(self.offsets[-1] + len(self.textures[-2]) + 1)
    else:
      self.offsets.appen(4)
    return
  def get_length(self):
    templength = 4 + 4 + 4 + self.numoffs.number * 8
    for x in self.fonts:
      templength = templength + len(x) + 1
    self.length = templength
    return self.length
  def write_to_file(self, file):
    file.write(self.magic)
    file.write(struct.pack('>I', self.length))
    self.numoffs.write_to_file(file)
    tempOffset = self.numoffs.number * 4
    for x in range(len(self.offsets)):
      file.write(struct.pack('>I', tempOffset))
      self.offsets[x] = tempOffset
      tempOffset = tempOffset + len(self.fonts[x]) + 1
    for x in self.fonts:
      file.write(x)
      file.write(struct.pack('s', '\x00'))
    return

class BRLYT_txl1:
  def __init__(self):
    self.magic = "txl1"
    self.numoffs = BRLYT_Numoffs()
    self.offsets = []
    self.textures = []
  def eat_tag(self, file, offset):
    self.magic, self.length = struct.unpack('>4sI', file[offset:offset+8])
    self.numoffs.eat_numoffs(file, offset+8)
    for x in range(self.numoffs.number):
      ''' Grab texture name '''
      offs, unknown = struct.unpack('>II', file[offset+8+4+x*8:offset+8+4+x*8+8])
      self.offsets.append(offs)
      texture = nullterm(file[offset+12+self.offsets[x]:])
      self.textures.append(texture)
    return
  def show_tag(self):
    print "Magic: %s" % self.magic
    print "Length: %08x" % self.length
    self.numoffs.show_numoffs()
    for x in range(len(self.textures)):
      print "Texture: %s offset: %08x" % ( self.textures[x] , self.offsets[x] )
    return
  def add_texture(self, texture):
    self.textures.append(texture)
    self.numoffs.add()
    if len(self.textures) > 1:
      self.offsets.append(self.offsets[-1] + len(self.textures[-2]) + 1)
    else:
      self.offsets.append(4)
    return
  def get_length(self):
    templength = 4 + 4 + 4 + self.numoffs.number * 8
    for x in self.textures:
      templength = templength + len(x) + 1
    self.length = templength
    return self.length
  def write_to_file(self, file):
    file.write(self.magic)
    file.write(struct.pack('>I', self.length))
    self.numoffs.write_to_file(file)
    tempOffset = self.numoffs.number * 4
    for x in range(len(self.offsets)):
      file.write(struct.pack('>I', tempOffset))
      self.offsets[x] = tempOffset
      tempOffset = tempOffset + len(self.textures[x]) + 1
    for x in self.textures:
      file.write(x)
      file.write(struct.pack('s', "\0"))
    return

class BRLYT_lyt1:
  def __init__(self):
    self.magic = "lyt1"
    self.length = 0x14
    self.a = 1
    self.pad1 = 0
    self.pad2 = 0
    self.pad3 = 0
    self.width = 608.0
    self.height = 456.0
  def eat_tag(self, file, offset):
    self.magic, self.length = struct.unpack('>4sI', file[offset:offset+8])
    self.a, self.pad1, self.pad2, self.pad3 = struct.unpack('>4B', file[offset+0x08:offset+0x08+4])
    self.width, self.height = struct.unpack('>ff', file[offset+0x0C:offset+0x0C+8])
    return
  def show_tag(self):
    print "Magic: %s" % self.magic
    print "Length: %08x" % self.length
    print "a: %02x" % self.a
    print "width: %f" % self.width
    print "height: %f" % self.height
    return
  def get_texoffset(self, texture):
    texoffset = -1
    for x in range(len(self.textures)):
      if self.textures[x] == texture:
        texoffset = x - 1
    return texoffset
  def get_length(self):
    self.length = 4 + 4 + 1 + 1 + 1 + 1 + 4 + 4
    return self.length
  def write_to_file(self, file):
    file.write(self.magic)
    file.write(struct.pack('>I', self.length))
    file.write(struct.pack('>B', self.a))
    file.write(struct.pack('>B', self.pad1))
    file.write(struct.pack('>B', self.pad2))
    file.write(struct.pack('>B', self.pad3))
    file.write(struct.pack('>f', self.width))
    file.write(struct.pack('>f', self.width))
    return

class BRLYT_Header:
  def __init__(self):
    self.data = []
  def eat_header(self, buffer, offset):
    self.magic, self.length = struct.unpack('>4sI', buffer[offset:offset+8])
    return
  def show_header(self, offset):
    print "Offset: %08x" % offset
    print "Magic: %s" % self.magic
    print "Length: %08x" % self.length
    return

class BRLYT:
  def __init__(self):
    self.tags_filled = 0
    self.data = []
    self.magic = "RLYT"
    self.version = 0xfeff0101
    self.offset = 0x10
    self.chunks = 0x0000
    self.tags = { }
  def grab_brlyt(self, file):
    for x in file:
      self.data.append(x)
    return
  def eat_brlyt(self, file):
    file_offset = 0
    self.magic, self.version = struct.unpack('>4sI', file[0x00:0x08])
    self.length, self.offset, self.count = struct.unpack('>IHH', file[0x08:0x10])
    file_offset = 0x10
    tempHeader = BRLYT_Header()
    for x in range(self.count):
      tempHeader.eat_header(file, file_offset)
      ''' DO BIG CASE IF FOR TYPE '''
      if tempHeader.magic == "lyt1":
        self.tags[x] = BRLYT_lyt1()
      elif tempHeader.magic == "txl1":
        self.tags[x] = BRLYT_txl1()
      elif tempHeader.magic == "fnl1":
        self.tags[x] = BRLYT_fnl1()
      elif tempHeader.magic == "mat1":
        self.tags[x] = BRLYT_mat1()
      elif tempHeader.magic == "pan1":
        self.tags[x] = BRLYT_pan1()
      elif tempHeader.magic == "pas1":
        self.tags[x] = BRLYT_pas1()
      elif tempHeader.magic == "pae1":
        self.tags[x] = BRLYT_pae1()
      elif tempHeader.magic == "wnd1":
        self.tags[x] = BRLYT_wnd1()
      elif tempHeader.magic == "bnd1":
        self.tags[x] = BRLYT_bnd1()
      elif tempHeader.magic == "pic1":
        self.tags[x] = BRLYT_pic1()
      elif tempHeader.magic == "txt1":
        self.tags[x] = BRLYT_txt1()
      elif tempHeader.magic == "grp1":
        self.tags[x] = BRLYT_grp1()
      elif tempHeader.magic == "grs1":
        self.tags[x] = BRLYT_grs1()
      elif tempHeader.magic == "gre1":
        self.tags[x] = BRLYT_gre1()
      else:
        print "BAD TAG"
        break
      self.tags[x].eat_tag(file, file_offset)
      file_offset = file_offset + self.tags[x].length
    self.tags_filled = self.chunks
    return
  def get_texoffset(self, texture):
    texoffset = self.tags[1].get_texoffset(texture)
    return texofffset
  def add_material(self, material, texture):
    texoffset = self.get_texoffset(texture)
    if texoffset == -1:
      print "texture not found in txl1"
      return
    for x in range(self.tags_filled):
      if isinstance(self.tags[x], BRLYT_mat1):
        self.tags[x].add_material(material, texoffset)
    return
  def add_grp1(self):
    self.tags[self.tags_filled] = BRLYT_grp1()
    self.tags_filled = self.tags_filled + 1
  def add_txt1(self):
    self.tags[self.tags_filled] = BRLYT_txt1()
    self.tags_filled = self.tags_filled + 1
  def add_pic1(self):
    self.tags[self.tags_filled] = BRLYT_pic1()
    self.tags_filled = self.tags_filled + 1
  def add_pae1(self):
    self.tags[self.tags_filled] = BRLYT_pae1()
    self.tags_filled = self.tags_filled + 1
  def add_pas1(self):
    self.tags[self.tags_filled] = BRLYT_pas1()
    self.tags_filled = self.tags_filled + 1
  def add_pan1(self):
    self.tags[self.tags_filled] = BRLYT_pan1()
    self.tags_filled = self.tags_filled + 1
  def add_mat1(self):
    self.tags[self.tags_filled] = BRLYT_mat1()
    self.tags_filled = self.tags_filled + 1
  def add_txl1(self):
    self.tags[self.tags_filled] = BRLYT_txl1()
    self.tags_filled = self.tags_filled + 1
    return
  def add_lyt1(self):
    self.tags[self.tags_filled] = BRLYT_lyt1()
    self.tags_filled = self.tags_filled + 1
    return
  def add_texture(self, texture):
    self.tags[1].add_texture(texture)
    return
  def add_font(self, font):
    self.tags[2].add_font(font)
    return
  def write_brlyt(self, filename):
    templength = 4 + 4 + 4 + 2 + 2
    for x in range(self.tags_filled):
      templength = templength + self.tags[x].get_length()
    self.length = templength
    file = open(filename, 'wb')
    if file:
      file.write(self.magic)
      file.write(struct.pack('>I', self.version))
      file.write(struct.pack('>I', self.length))
      file.write(struct.pack('>H', self.offset))
      file.write(struct.pack('>H', self.chunks))
      for x in range(len(self.tags)):
        self.tags[x].write_to_file(file)
      file.close()
    else:
      print "could not open file for write"
    return
  def show_brlyt(self):
    print "Magic: %s" % self.magic
    print "Version: %08x" % self.version
    print "File size: %08x" % self.length
    print "Header size: %04x" % self.offset
    print "Chunk count: %04x" % self.count
    for x in range(len(self.tags)):
      self.tags[x].show_tag()
      print
    return

if len(sys.argv) != 2:
    print 'Usage: python brlyt.py <filename>'
    sys.exit(1)

f = open(sys.argv[1], 'rb')
if f:
    rlyt = f.read()
    f.close()
else:
    print "could not open file"

brlyt = BRLYT()
brlyt.eat_brlyt(rlyt)
brlyt.show_brlyt()
brlyt.write_brlyt("testout.brlyt")

''' TEST FOR WRITING A BRLYT FROM SCRATCH ''' '''
brlyt2 = BRLYT()
brlyt2.add_lyt1()
brlyt2.add_txl1()
brlyt2.add_texture("texture1.tpl")
brlyt2.add_mat1()
brlyt2.add_material("material1", "texture1.tpl")
brlyt2.add_pan1()
brlyt2.add_pas1()
brlyt2.add_pic1()
brlyt2.add_pae1()
brlyt2.add_grp1()
brlyt2.write_brlyt("testout.brlyt")
''' '''END TEST FOR BRLYT WRITING '''
