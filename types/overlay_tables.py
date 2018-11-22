import struct

#https://wiki.cloudmodding.com/oot/Overlay_Tables

class ParticleOverlayEntry(object):
	'''
	Format:
		xxxxxxxx yyyyyyyy aaaaaaaa bbbbbbbb
		rrrrrrrr pppppppp ????????
		
		x y: Start/End Virtual Rom addresses of the particle effect's file
		a b: Start/End Virtual Ram addresses of the particle effect's file
		r: Ram address of the overlay, when loaded into ram. Set to 0 in Rom
		p: ?, possibly a pointer to the initialization routine
		?: Unknown, set to 0x01000000 in Rom
	'''
	size = 7*4
	
	def __init__(self,raw:bytes, addr:int):
		if len(raw) != self.size:
			raise Exception("Invalid size for ParticleOverlayEntry")

		self.addr = addr
		x,y,a,b,r,p,ukn = struct.unpack('>'+'I '*7,raw)

		self.vrom_start 	= x
		self.vrom_end 		= y
		self.vram_start 	= a
		self.vram_end 		= b
		self.rom_loc		= r
		self.ptr 			= p
		self.ukn 			= ukn

class ActorOverlayEntry(object):
	'''
	Format
		xxxxxxxx yyyyyyyy aaaaaaaa bbbbbbbb
		rrrrrrrr iiiiiiii nnnnnnnn vvvvcc00
		
		This breaks down into-
		x y: Start/End Virtual Rom addresses of the actor file
		a b: Start/End Virtual Ram addresses of the actor file
		r: Ram address of actor file (00000000 if overlay isn't loaded, or if in ROM)
		i: Virtual Ram address of the start of the actor instance initialization variables, located within the file
		n: Address of actor filename (Debug ROM only, value is 0 in commercial releases)
		v: Allocation Type, affects how overlay is allocated. See below for values
		c: Number of actor instances of this type currently loaded (ram only)

	Allocation Type Values
		00 performs a "low to high" address allocation (high address volatility), unloading the overlay if no instances of that actor exist
		01 performs a "high to low" address allocation (low address volatility), reserving a fixed space for all overlays of this type until the scene is destructed. Only one overlay of this type can ever be loaded at once. The pointer to this space is located at Global Context + 0x1C60
		02 performs a "high to low" address allocation (low address volatility), keeping the overlay in ram until the scene is destructed
	Note: The record for Link's actor in rom (the first record in the table) only sets the vram address that points to the start of the variable info for Link's actor, and the actor file name pointer if it's the Debug Rom.
	'''

	size = 4*8

	def __init__(self,raw:bytes, addr:int):
		if len(raw) != self.size:
			raise Exception("Invalid size for ParticleOverlayEntry")

		self.addr = addr

		x,y,a,b,r,i,n,v,c,_ = struct.unpack('>' + 'I'*7 + 'H' + 'B'*2,raw)

		self.vrom_start 	= x
		self.vrom_end 		= y
		self.vram_start 	= a
		self.vram_end 		= b
		self.rom_loc		= r
		self.vram_var		= i
		self.filename_off	= n
		self.alloc_type		= v
		self.inst_cnt		= c


class GameStateEntry(object):
	'''
	r	/* 0x00 */ uint RamStart; //location of overlay in ram, or 0 in rom

	x	/* 0x04 */ int VRomStart; //if applicable
	y	/* 0x08 */ int VRomEnd;   //if applicable
	a	/* 0x0C */ int VRamStart; //if applicable	
	b	/* 0x10 */ int VRamEnd;   //if applicable
 	
 	u	/* 0x14 */ uint unknown2;
	s	/* 0x18 */ ptr VRamInitialization; //initializes and executes the given context
 	t	/* 0x1C */ ptr VRamDeconstructor; //"deconstructs" the context, and sets the next context to load
		
	_	/* 0x20-0x2B */ //unknown
		
	w	/* 0x2C */ int AllocateSize; //Size of initialized instance of the overlay
	'''
	size = 0x30
	def __init__(self,raw:bytes, addr:int):
		if len(raw) != self.size:
			raise Exception("Invalid size for ParticleOverlayEntry")

		self.addr = addr
		
		r, x,y,a,b, u,s,t = struct.unpack('>' +'I'*8,raw[:0x20])
		w = struct.unpack(">I",raw[0x2c:])

		self.vrom_start 	= x
		self.vrom_end 		= y
		self.vram_start 	= a
		self.vram_end 		= b

		self.ram_start		= r
		self.vram_ctor		= s
		self.vram_dtor		= t

		self.alloc_size		= w

class MapMarkEntry(object):
	'''
	r 	/* 0x00 */ void*  RamStart; // 0 in rom, or when not loaded
	 	
	x 	/* 0x04 */ int    VRomStart; 
	y 	/* 0x08 */ int    VRomEnd;   
	a 	/* 0x0C */ int    VRamStart; 
	b 	/* 0x10 */ int    VRamEnd;  
	
	c 	/* 0x14 */ void** DungeonMarkData; //Points to array storing start of data for dungeons 0-9
	'''

	size = 0x18

	def __init__(self,raw:bytes, addr:int):
		if len(raw) != self.size:
			raise Exception("Invalid size for ParticleOverlayEntry")

		self.addr = addr
		
		r, x,y,a,b, c = struct.unpack('>'+'I'*6,raw)

		self.vrom_start 	= x
		self.vrom_end 		= y
		self.vram_start 	= a
		self.vram_end 		= b

		self.ram_start		= r
		self.markdata		= c

class PlayerPauseEntry(object):
	'''
	rrrrrrrr xxxxxxxxx yyyyyyyy aaaaaaaa
	bbbbbbbb ????????? ffffffff

	r = Ram Start, when loaded, or 0 in Rom
	x = VRom Start
	y = VRom End
	a = VRam Start
	b = VRam End
	? = ?, 0 in rom
	f = Ram location of file name
	'''
	size = 7 * 4

	def __init__(self,raw:bytes, addr:int):
		if len(raw) != self.size:
			raise Exception("Invalid size for ParticleOverlayEntry")

		self.addr = addr

		r, x,y,a,b, _, f = struct.unpack('>'+'I'*7,raw)

		self.vrom_start 	= x
		self.vrom_end 		= y
		self.vram_start 	= a
		self.vram_end 		= b

		self.ram_start		= r
		self.ram_file_name	= f