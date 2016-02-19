import SIDCrypto
import os

## Classe mère ("abstraite") pour le stockage d'infos sur les fichiers, répertoires ou liens
# n'est pas censée être instanciée
# @path : chemin relatif
# si size ou modTime non donnés au constructeur,
# recherche de la valeur
class AbstractFile:
	def __init__(self,filePath,currPath='.',size=-1,modTime=-1):
		self.path = filePath		
		if size < 0 or modTime < 0:
			prop = os.lstat(os.path.join(currPath,filePath))
		if size < 0: 
			self.size = prop.st_size
		else : 
			self.size = size
		if modTime < 0: 
			self.modTime = prop.st_mtime
		else: 
			self.modTime = modTime

	def getPath(self):
		return self.path
	
	def getSize(self):
		return self.size

	def getModTime(self):
		return self.modTime	

	# before encoding in json
	def encode(self):
		if isinstance(self, AbstractFile):
			return {'type' : 'AbstractFile',
				'path' : self.path,
				'size' : self.size,
				'modTime' : self.modTime}
		raise TypeError(repr(o)+" is not JSON serializable")
	
	# to decode from json
	# usage: json.loads(obj, object_hook = AbstractFile.decode)
	@staticmethod
	def decode(dic):
		if dic['type'] == 'AbstractFile':
			print("DEBUG : appel de AbstractFile.decode() sur {0}".format(dic))
			return AbstractFile(dic['path'],
					 currPath=None,
					 size=dic['size'],
					 modTime=dic['modTime'])
		return None
	
	# before encoding in json (any type)
	# usage: json.dumps(obj, default=AbstractFile.universalEncode, sort_keys=True, indent=2)
	@staticmethod
	def universalEncode(obj):
		if isinstance(obj, AbstractFile):
			return obj.encode()
		else:
			#print("DEBUG : unknown type in universalEncode. Handled as basic type")
			return obj

	# to decode from json (any type)
	# usage: json.loads(data, object_hook = AbstractFile.UniversalDecode)	
	@staticmethod
	def universalDecode(data, rep_path='.'):
		TYPES = {'AbstractFile' : AbstractFile, 'BasicFile' : BasicFile, 'BigFile' : BigFile, 'SmallFile' : SmallFile, 'SymbolicLink': SymbolicLink, 'Directory' : Directory}
		if type(data) == dict:
			try:
				obj = TYPES[data['type']].decode(data)
				return obj 
			except KeyError:
				#print("DEBUG : unknown type, dict handled recursively in universalDecode")
				obj_dic = {}
				for k in data:
					obj_dic[k] = AbstractFile.universalDecode(data[k])
				return data
		elif type(data) == list:
			l = []
			for e in data:
				l.append(AbstractFile.universalDecode(e))
			return l
		else:
			return data

# Pour le stockage d'infos sur les fichiers (grands ou petits)
# SHOULD NOT BE INSTANCIATED (see BigFile and SmallFile)
# si hash, size, modTime ou mode non donnés au constructeur,
# recherche ou calcul de la valeur
class BasicFile(AbstractFile):
	def __init__(self,filePath,currPath='.',size=-1,modTime=-1,mode=None):
		AbstractFile.__init__(self,filePath,currPath,size,modTime)
		if size < 0 or modTime < 0 or mode < 0:
			prop = os.lstat(os.path.join(currPath,filePath))
		if mode == None: 
			self.mode = prop.st_mode
		else: 
			self.mode = mode
	
	def getMode(self):
		return self.mode

	# before encoding in json
	def encode(self):
		if isinstance(self, BasicFile):
			dic = AbstractFile.encode(self)  ### ?
			dic['type'] = 'BasicFile'
			dic['mode'] = self.mode
			return dic
		raise TypeError(repr(o)+" is not JSON serializable")

	# to decode from json
	@staticmethod
	def decode(dic):
		if dic['type'] == 'BasicFile':
			bf = BasicFile(dic['path'], 
						   currPath=None, 
						   size=dic['size'], 
						   modTime=dic['modTime'], 
						   mode=dic['mode'],)
			return bf
		return dic

class BigFile(BasicFile):
	def __init__(self,filePath,serverName,hash=None,currPath='.',size=-1,modTime=-1,mode=None,key=None):
		BasicFile.__init__(self,filePath,currPath='.',size=-1,modTime=-1,mode=None)
		self.serverName = severName
		if hash == None:
			self.hash = crypto.hash(os.path.join(currPath,filePath), hash_file = True)
		else: 
			self.hash = hash
		if key == None:
			## TODO
		else:
			self.key = key

	# before encoding in json
	def encode(self):
		if isinstance(self, BigFile):
			dic = BasicFile.encode(self)  ### ?
			dic['type'] = 'BigFile'
			dic['hash'] = self.hash
			dic['serverName'] = self.serverName
			dic['key'] = self.key
			return dic
		raise TypeError(repr(o)+" is not JSON serializable")

	# to decode from json
	@staticmethod
	def decode(dic):
		if dic['type'] == 'BigFile':
			bf = BigFile(dic['path'], 
						   dic['serverName'],
						   hash=dic['hash'],
						   currPath=None, 
						   size=dic['size'], 
						   modTime=dic['modTime'], 
						   mode=dic['mode'],
						   key=dic['key'])
			return bf
		return dic

	def getHash(self):
		return self.hash

	def getServerName(self):
		return self.serverName

	def getKey(self):
		return self.key

	def compareToLocal(self, localHash):
		return self.hash == localHash

class SmallFile(BasicFile):
	def __init__(self,filePath,content=None,currPath='.',size=-1,modTime=-1,mode=None):
		BasicFile.__init__(self,filePath,currPath='.',size=-1,modTime=-1,mode=None)
		if content==None:
			o = open(os.path.join(currPath,filePath),'rb')
			self.content = o.read()
		else:
			self.content = content

	def getContent(self):
		return self.content

	# before encoding in json
	def encode(self):
		if isinstance(self, SmallFile):
			dic = BasicFile.encode(self)  ### ?
			dic['type'] = 'SmallFile'
			dic['content'] = self.content
			return dic
		raise TypeError(repr(o)+" is not JSON serializable")

	# to decode from json
	@staticmethod
	def decode(dic):
		if dic['type'] == 'SmallFile':
			sf = SmallFile(dic['path'], 
						   content=dic['content'],
						   currPath=None, 
						   size=dic['size'], 
						   modTime=dic['modTime'], 
						   mode=dic['mode'])
			return sf
		return dic

	def compareToLocal(self, localContent):
		return self.content == localContent

# Pour le stockage d'infos sur les liens symboliques
# si size, modTime ou adresse de la cible non donnés au constructeur,
# recherche de la valeur
class SymbolicLink(AbstractFile):
	def __init__(self,filePath,currPath='.',size=-1,modTime=-1,linkURL=None):
		AbstractFile.__init__(self,filePath,currPath,size,modTime)
		if linkURL == None: 
			self.linkURL = os.readlink(os.path.join(currPath,filePath))
		else: 
			self.linkURL = linkURL

	def getLinkURL(self):
		return self.linkURL

	# before encoding in json
	def encode(self):
		if isinstance(self, SymbolicLink):
			dic = AbstractFile.encode(self)
			dic['type'] = 'SymbolicLink'
			dic['linkURL'] = self.linkURL
			return dic
		raise TypeError(repr(o)+" is not JSON serializable")

	# to decode from json
	@staticmethod
	def decode(dic):
		if dic['type'] == 'SymbolicLink':
			sl = SymbolicLink(dic['path'],
					  currPath=None,
					  size=dic['size'],
					  modTime=dic['modTime'],
					  linkURL=dic['linkURL'])
			return sl
		return dic

# Pour le stockage d'infos sur les répertoires
# si size, modTime ou mode non donnés au constructeur,
# recherche de la valeur
class Directory(AbstractFile):
	def __init__(self,filePath,currPath='.',size=-1,modTime=-1,mode=None):
		AbstractFile.__init__(self,filePath,currPath,size,modTime)
		if mode == None: 
			prop = os.lstat(os.path.join(currPath, filePath))
			self.mode = prop.st_mode
		else: self.mode = mode

	def getMode(self):
		return self.mode
	
	# before encoding in json
	def encode(self):
		if isinstance(self, Directory):
			dic = AbstractFile.encode(self)
			dic['type'] = 'Directory'
			dic['mode'] = self.mode
			return dic
		raise TypeError(repr(o)+" is not JSON serializable")

	# to decode from json
	@staticmethod
	def decode(dic):
		if dic['type'] == 'Directory':
			di = Directory(dic['path'],
						   currPath=None,
						   size=dic['size'],
						   modTime=dic['modTime'],
						   mode=dic['mode'])
			return di
		return dic
