from enum import Enum
import struct

def I(x:bytes): return struct.unpack(">I",x)[0]
def PI(x:bytes): return struct.pack(">I",x)

class RelocType(Enum):
	R_MIPS_32	= 2
	R_MIPS_26	= 4
	R_MIPS_HI16	= 5
	R_MIPS_LO16	= 6

name = {
	RelocType.R_MIPS_32		: '32 bit pointer',
	RelocType.R_MIPS_26		: 'jump target',
	RelocType.R_MIPS_HI16	: 'lui/ori pair high 16 bits',
	RelocType.R_MIPS_LO16	: 'lui/ori pair low 16 bits',
}

class EnumLoc(Enum):
	text 	= 1
	data 	= 2
	rodata 	= 3
	bss 	= 4

class Reloc(object):
	def __init__(self, raw):
		self.loc = EnumLoc(raw>>30)
		self.type = RelocType(raw>>24 & 0x3f)
		self.off = raw & 0x00ffffff
	def toRaw(self):
		return PI(self.loc.value<<30 | self.type.value<<24 | self.off)
	def __repr__(self):
		return f'{name[self.type]}: {str(self.loc)[8:]}+0x{self.off:06x}'

class Overlay(object):
	def __init__(self, name, raw, vram):
		self.name = name
		self.vram = vram
		
		def getWord(off):
			return I(raw[off:off+4])

		seek = getWord(len(raw)-4)
		self.table = len(raw) - seek

		textsize    = getWord(self.table +  0)
		datasize    = getWord(self.table +  4)
		rodatasize  = getWord(self.table +  8)
		bsssize     = getWord(self.table + 12)
		reloccnt    = getWord(self.table + 16)

		seek = 0
		def read(size):
			nonlocal seek
			ret = raw[seek:seek+size]
			seek += size
			return ret

		self.text = read(textsize)
		self.data = read(datasize)
		self.rodata = read(rodatasize)
		self.bss = b''
		if bsssize:
			self.bss = read(bsssize)

		raw_reloc = raw[self.table+20:self.table+20+reloccnt*4]

		self.reloc = [Reloc(I(raw_reloc[i:i+4])) for i in range(0,len(raw_reloc),4)]

	def getSectionByName(self,section):
		return {
			'text': self.text,
			'data': self.data,
			'rodata': self.rodata,
			'bss': self.bss,
		}[section]

	def toRaw(self):
		preamble = self.text + self.data + self.rodata + self.bss
		table = PI(len(self.text)) + PI(len(self.data)) + PI(len(self.rodata)) + PI(len(self.bss)) + PI(len(self.reloc))
		reloc = b''
		for re in self.reloc:
			reloc = reloc + re.toRaw()
		seek = PI(len(table) + len(reloc) + 4)
		return preamble + table + reloc + seek
