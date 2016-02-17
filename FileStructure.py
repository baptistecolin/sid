import SIDCrypto
import os

# @path : chemin depuis le repertoire sauvegarde
class StructureFile:
	def __init__(self,path,size=-1,modTime=-1):
		self.path = path
		prop = os.lstat(f)
		if size < 0: 
			self.size = prop.st_size
		else : 
			self.size = size
		if modTime < 0: 
			self.modTime = prop.st_mtime
		else: 
			self.modTime = modTime

	def getHash(self):
		return self.hash
	
	def getSize(self):
		return self.size

	def getModTime(self):
		return self.modTime
	
	# before encoding in json
	def encode(self):
		if isinstance(self, StructureFile):
			return {'__StructureFile__' : True,
				'path' : self.path,
				'size' : self.size,
				'modTime' : self.modTime}
		raise TypeError(repr(o)+" is not JSON serializable")
	
	# to decode from json
	# usage: json.loads(obj, object_hook = StructureFile.decode)
	@staticmethod
	def decode(dic):
		if '__StructureFile__' in dic:
			return StructureFile(dic['path'],
				     dic['size'],
				     dic['modTime'])
		return None
	

class BasicFile(StructureFile):
	def __init__(self,path,serverName,hash=None,size=-1,modTime=-1,mode=None):
		StructureFile.__init__(self,path,size,modTime)
		if hash == None:
			self.hash = crypto.hash(path, hash_file = True)
		else: 
			self.hash = hash
		prop = os.lstat(f)
		if mode == None: 
			self.mode = prop.st_mode
		else: 
			self.mode = mode
		self.serverName = serverName
	
	def getMode(self):
		return self.mode

	def getServerName(self):
		return self.serverName

	def getHash(self):
		return self.hash

	# before encoding in json
	def encode(self):
		if isinstance(self, BasicFile):
			dic = StructureFile.encode(self)  ### ?
			dic['__BasicFile__'] = True
			dic['mode'] = self.mode
			dic['serverName'] = self.serverName
			dic['hash'] = self.hash
			return dic
		raise TypeError(repr(o)+" is not JSON serializable")

	# to decode from json
	@staticmethod
	def decode(dic):
		if '__BasicFile__' in dic:
			dic['__StructureFile__'] = True
			bf = StructureFile.decode(dic)
			bf.mode = dic['mode']
			bf.serverName = dic['serverName']
			return bf
		return dic

class SymbolicLink(StructureFile):
	def __init__(self,path,size=-1,modTime=-1,linkURL=None):
		StructureFile.__init__(self,path,size,modTime)
			if linkURL == None: self.linkURL = os.readlink(path)
			else: self.linkURL = linkURL

	def getLinkURL(self):
		return self.linkURL

	# before encoding in json
	def encode(self):
		if isinstance(self, SymbolicLink):
			dic = StructureFile.encode(self)
			dic['__SymbolicLink__'] = True
			dic['linkURL'] = self.linkURL
			return dic
		raise TypeError(repr(o)+" is not JSON serializable")

	# to decode from json
	@staticmethod
	def decode(dic):
		if '__SymbolicLink__' in dic:
			dic['__StructureFile__'] = True
			sl = StructureFile.decode(dic)
			sl.linkURL = dic['linkURL']
			return sl
		return dic

class Directory(StructureFile):
	def __init__(self,path,size=-1,modTime=-1,mode=None):
		StructureFile.__init__(self,path,size,modTime)
		if mode == None: 
			prop = os.lstat(f)
			self.mode = prop.st_mode
		else: self.mode = mode

	def getMode(self):
		return self.mode
	
	# before encoding in json
	def encode(self):
		if isinstance(self, Directory):
			dic = StructureFile.encode(self)
			dic['__Directory__'] = True
			dic['mode'] = self.mode
			return dic
		raise TypeError(repr(o)+" is not JSON serializable")

	# to decode from json
	@staticmethod
	def decode(dic):
		if '__Directory__' in dic:
			dic['__StructureFile__'] = True
			di = StructureFile.decode(dic)
			di.mode = dic['mode']
			return di
		return dic
