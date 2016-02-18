import SIDCrypto
import os

## Classe mère ("abstraite") pour le stockage d'infos sur les fichiers, répertoires ou liens
# n'est pas censée être instanciée
# @path : chemin relatif
# si size ou modTime non donnés au constructeur,
# recherche de la valeur
class AbstractFile:
	def __init__(self,path,size=-1,modTime=-1):
		self.path = path
		prop = os.lstat(path)
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
		if dic['type'] == 'AbstractFile:
			return AbstractFile(dic['path'],
				     dic['size'],
				     dic['modTime'])
		return None
    
    TYPES = {'AbstractFile' : AbstractFile, 
             'BasicFile' : BasicFile,
             'SymbolicLink': SymbolicLink, 
             'Directory' : Directory}

    # before encoding in json (any type)
    # usage: json.dumps(obj, default=FileStructure.universalEncode, sort_keys=True, indent=2)
    def universalEncode(obj):
	    if isinstance(obj, AbstractFile):
	    	return obj.encode()
	    else:
	    	print("DEBUG appel de universalEncode sur un type inconnu. Type de base ?")
	       	return obj

    # to decode from json (any type)
    # usage: json.loads(data, object_hook = AbstractFile.UniversalDecode)    
    @staticmethod
    def universalDecode(dic):
        return TYPES[dic['type']].decode(dic)
	
# Pour le stockage d'infos sur les fichiers
# si hash, size, modTime ou mode non donnés au constructeur,
# recherche ou calcul de la valeur
class BasicFile(AbstractFile):
	def __init__(self,path,serverName,hash=None,size=-1,modTime=-1,mode=None):
		AbstractFile.__init__(self,path,size,modTime)
		if hash == None:
			self.hash = crypto.hash(path, hash_file = True)
		else: 
			self.hash = hash
		prop = os.lstat(hash)
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
			dic = AbstractFile.encode(self)  ### ?
			dic['type'] = 'BasicFile'
			dic['mode'] = self.mode
			dic['serverName'] = self.serverName
			dic['hash'] = self.hash
			return dic
		raise TypeError(repr(o)+" is not JSON serializable")

	# to decode from json
	@staticmethod
	def decode(dic):
		if 'type' == 'BasicFile' in dic:
			bf = BasicFile(dic['path'], 
                           dic['serverName'], 
                           dic['hash'], 
                           dic['size'], 
                           dic['modTime'], 
                           dic['mode'])
			return bf
		return dic

## TODO : SmallFile ??

# Pour le stockage d'infos sur les liens symboliques
# si size, modTime ou adresse de la cible non donnés au constructeur,
# recherche de la valeur
class SymbolicLink(AbstractFile):
	def __init__(self,path,size=-1,modTime=-1,linkURL=None):
		AbstractFile.__init__(self,path,size,modTime)
		if linkURL == None: 
			self.linkURL = os.readlin(path)
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
		if 'type' == 'SymbolicLink':
			sl = SymbolicLink(dic['path'],
                              dic['size'],
                              dic['modTime'],
                              dic['linkURL'])
			return sl
		return dic

# Pour le stockage d'infos sur les répertoires
# si size, modTime ou mode non donnés au constructeur,
# recherche de la valeur
class Directory(AbstractFile):
	def __init__(self,path,size=-1,modTime=-1,mode=None):
		AbstractFile.__init__(self,path,size,modTime)
		if mode == None: 
			prop = os.lstat(path)
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
		if 'type' == 'Directory':
			di = Directory(dic['path'],
                           dic['size'],
                           dic['modTime'],
                           dic['mode'])
			return di
		return dic





