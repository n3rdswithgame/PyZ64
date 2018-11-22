from enum import Enum,auto
import json
import os
import struct

def btos(b:bytes): return str(b)[2:-1]
def relToAbsPath(path:str): return os.path.dirname(__file__) + '/' + path

class Versions(Enum):
	OoT1_0 	= 0
	OoT1_1 	= auto()
	OoT1_2 	= auto()
	OoTGC	= auto()
	OoTMQ	= auto()
	OoTDB	= auto()
	MM1_0	= auto()
	MM1_1	= auto()
	MMENG	= auto()
	MMGCE	= auto()
	MMGCJ	= auto()
	MMDBG	= auto()
	ALL 	= auto()
#version specific value
class VSV(object):
	def __init__(self, a=None, o1_0 = None, o1_1=None, o1_2=None, ogc=None, omq=None, odbg=None, m1_0=None, m1_1=None, meng=None, mgce=None, mgcj=None, mdbg=None):
		self.dict = {
			Versions.OoT1_0 	: o1_0,
			Versions.OoT1_1 	: o1_1,
			Versions.OoT1_2 	: o1_2,
			Versions.OoTGC 		: ogc,
			Versions.OoTMQ 		: omq,
			Versions.OoTDB 		: odbg,
			Versions.MM1_0 		: m1_0,
			Versions.MM1_1 		: m1_1,
			Versions.MMENG 		: meng,
			Versions.MMGCE 		: mgce,
			Versions.MMGCJ 		: mgcj,
			Versions.MMDBG 		: mdbg,
			Versions.ALL 		: a
		}

	def __getitem__(self, key:Versions):
		return self.dict.get(key, None)
	def __repr__(self):
		return str({key:val for key,val in self.dict.items() if val is not None})
class VSVEncoder(json.JSONEncoder):
	def default(self,o):
		mapping = {
			Versions.OoT1_0 	: 'o1_0',
			Versions.OoT1_1 	: 'o1_1',
			Versions.OoT1_2 	: 'o1_2',
			Versions.OoTGC 		: 'ogc',
			Versions.OoTMQ 		: 'omq',
			Versions.OoTDB 		: 'odbg',
			Versions.MM1_0 		: 'm1_0',
			Versions.MM1_1 		: 'm1_1',
			Versions.MMENG 		: 'meng',
			Versions.MMGCE 		: 'mgce',
			Versions.MMGCJ 		: 'mgcj',
			Versions.MMDBG 		: 'mdbg',
			Versions.ALL		: 'a'
		}
		if isinstance(o,VSV):
			return {mapping[k]:v for k,v in o.dict.items() if v is not None}
		return {'__{}__'.format(o.__class__.__name__): o.__dict__}
class PyZ64DirectoryRetriever(object):
	def __init__(self, d:dict, ver:Versions, key):
		self.d = d
		self.ver = ver
		self.accessingkey = key

	def __getitem__(self, key):
		if key not in self.d:
			print(self.d)
			print(key)
			return None
		val = self.d[key]
		if isinstance(val,VSV):
			if val[self.ver] is not None:
				return val[self.ver]
			else:
				return val[Versions.ALL]
		elif isinstance(val,dict):
			return PyZ64DirectoryRetriever(val,self.ver,key)
	def __repr__(self):
		return str({"ver":self.ver,"dict":self.d})

class PyZ64Directory(object):
	@staticmethod
	def load(filename):
		with open(relToAbsPath(filename)) as f:
			return PyZ64Directory(json.load(f))

	def __init__(self,vals:dict):
		self.dict = {key:{k:VSV(**v) for k,v in val.items()} for key,val in vals.items()}

	def __repr__(self):
		return str(self.dict)

	def keys(self):
		return self.dict.keys()

	def getRawDict(self):
		return self.dict

	def getRootRetriever(self, ver):
		return PyZ64DirectoryRetriever(self.dict,ver,'root')

	def save(self,filename):
		with open(relToAbsPath(filename),'w') as f:
			json.dump(self.dict,f,cls=VSVEncoder,indent='\t')

	def get(self,key,ver):
		return PyZ64Directory(self.dict[key],ver,key)



filetable = PyZ64Directory.load('json/filetable.json')
addr = PyZ64Directory.load('json/addr.json')
