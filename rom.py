from enum import Enum,auto
import json
import os
import struct

from .version import Versions, filetable, addr

def I(x:bytes): return struct.unpack(">I",x)[0]

class Endian(Enum):
	Big			= 0
	ByteSwapped	= auto()
	Little 		= auto()

	Z64			= Big
	V64			= ByteSwapped
	N64			= Little

class Language(Enum):
	JP		= 0
	ENG		= auto()
	PAL		= auto()

class RomHeader(object):
	def __init__(self, rom):
		#rom:Z64Rom defined below
		self.raw = rom.read(0,0x40)
		def get(off, size):
			return self.raw[off:off+size]
		def getI(off):
			tmp = get(off, 4)
			return I(tmp)

		self.PI_inits = getI(0)
		self.clockRate = getI(0x4)
		self.entryPoint = getI(0x8)
		self.releseaddr = getI(0xC)
		self.CRC1 = getI(0x10)
		self.CRC2 = getI(0x14)
		#0x18 - 0x20 unused
		self.name = str(self.raw[0x20:0x34])[2:-1]
		#0x34 - 0x38 unused
		self.mediaFormat = getI(0x38)
		self.cartID = self.raw[0x3c:0x3e]
		self.lang = chr(self.raw[0x3e])
		self.ver = self.raw[0x3f]

class Z64Rom(object):
	@staticmethod
	def open(filename):
		with open(filename,'rb') as filedescriptor:
			file = filedescriptor.read()
		return Z64Rom(file)

	def __init__(self, file:bytes, ver:Versions=Versions.OoT1_0):
		self.file = file
		endianchk = file[0:4]
		if endianchk == b'\x80\x37\x12\x40':
			self.endian = Endian.Big
		elif endianchk == b'\x37\x80\x40\x12':
			self.endian = Endian.ByteSwapped
		elif endianchk == b'\x40\x12\x37\x80':
			self.endian = Endian.Little
		else:
			raise Exception("Invalid n64 rom")


		self.header = RomHeader(self)
		if self.header.lang == 'E':
			self.lang = Language.ENG
		elif self.header.lang == 'J':
			self.lang = Language.JP


		self.ver = ver
		self.addr = addr.getRootRetriever(self.ver)
		tmp = filetable.getRootRetriever(self.ver)
		self.files = [ (tmp[file]["start"], tmp[file]["end"], file) for file in filetable.keys()]
		self.files.sort(key=lambda x: x[0])

	def read(self, off:int, size:int):
		pre  =             off  & 0b0011
		post = 4 - (size + off) & 0b0011

		start = off - pre
		end   = off + size + post

		ret = self.file[start:end]


		if self.endian == Endian.Big:
			return ret[pre : pre + size]

		ret = [x for i in range(0,len(ret),2) for x in (ret[i+1],ret[i])]

		if self.endian == Endian.ByteSwapped:
			return ret[pre : pre + size]

		ret = [x for i in range(0,len(ret),4) for x in (ret[i+2],ret[i+3],ret[i],ret[i+1])]

		return ret[pre : pre + size]

	def getContainingFile(self, vrom:int):
		if vrom > self.files[-1][1] or vrom < 0:
			raise Exception(f'vrom offset {vrom} is outside of the rom')
		low, high = 0, len(self.files)
		while True:
			mid = (low + high) // 2
			candidate = self.files[mid]
			if vrom < candidate[0]: #before candidate
				high = mid
			elif vrom >= candidate[1]: #after candidate
				low = mid
			else: #in the range candidate[0] <= vrom < candidate[1]
				return candidate[2]

	def getRawFile(self,filename:str):
		for start, end, file in self.files:
			if filename.lower() == file.lower():
				return self.read(start, end-start)
		raise Exception(f'{filename} not in the rom')
		

	def __getitem__(self,key):
		return self.addr[key]