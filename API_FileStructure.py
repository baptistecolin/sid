class AbstractFile:
	# "abstract" class
	subclasses: BasicFile, SymbolicLink, Directory
	constructor:
		non-optional arguments:
			str filePath
		optional arguments:
			str currPath
			int size
			int modTime
	attributes (non optional):
		str path
		int size
		int modTime
	attributes (optional):
		-
	methods:
		getters
		compareToLocal(self, currPath=None, filePath=None):
			@currPath : str
			@filePath : str
			returns bool
		encode(self):
			returns dic
		@staticmethod decode(dic)
			returns AbstractFile or None (abnormal use)
		@staticmethod universalEncode(obj)
			@obj : AbstractFile (normal use)
			returns AbstractFile (or subclass)
		@staticmethod universalDecode(data, rep_path='.')
			@data : dict, list or basic type (int, str...)
			@rep_path : str
			returns dict, list, basic type, AbstractFile or subclass

class BasicFile(AbstractFile):
	# "abstract" class
	subclasses: BigFile, SmallFile
	constructor:
		non-optional arguments:
			str filePath
		optional arguments:
			str currPath
			int size
			int modTime
			int mode
	attributes (non optional):
		str path
		int size
		int modTime
		int mode
	attributes (optional):
			- 
	methods:
		getters
		@inherited @staticmethod universalEncode, universalDecode		
		@override encode(self)
			returns dict
		@override @staticmethod decode(dic)
			@dic : dict (normal use)
			returns BasicFile (normal use)
		@override encode(self)
			returns dict
		@override compareToLocal(self, currPath=None, filePath=None, localHash=None, crypto=None, localContent=None, compareMode=True)
			@currPath : str
			@filePath : str
			@localHash : ? ### TODO
			@crypto : SIDCrypto
			@localContent : ? ### TODO
			@compareMode : bool
			returns bool
		
class BigFile(BasicFile(AbstractFile)):
	constructor:
		non-optional arguments:
			@filePath : str
			@serverName : str
			@sidKey : ? ### TODO
		optional arguments:
			@hash : ? ### TODO
			@crypto : SIDCrypto
			@currPath : str
			@size : int
			@modTime : int
			@mode : int
			
		attributes (non optional):
			str path
			int size
			int modTime
			int mode
			str serverName
			? hash ### TODO
			? sidKey ### TODO
		attributes (optional):
			-
		methods:
			getters
			@inherited compareToLocal
			@inherited @staticmethod universalEncode, universalDecode
			@override encode(self)
				returns dic
			@override @staticmethod decode(dic)
				@dic : dict (normal use)
				returns BigFile
			compareHash(self, localHash)
				@localHash : ? ### TODO
				returns bool

class SmallFile(BasicFile(AbstractFile)):
	constructor:
		non-optional arguments:
			@filePath : str
		optional arguments:
			@currPath : str
			@content : ? ### TODO
			@size : int
			@modTime : int
			@mode : int
	attributes (non-optional):
		str path
		int size
		int modTime
		int mode
		? content ### TODO str ? sinon pb dans json.dumps
	attributes (optional):
		-
	methods:
		@inherited compareToLocal
		@inherited @staticmethod universalEncode, universalDecode
		@override encode
		@override @staticmethod decode
		compareContent(self, localContent)
			@localContent : ? ### TODO
			returns bool

class SymbolicLink(AbstractFile):
	constructor:
		non-optional arguments:
			@filePath : str
		optional arguments:
			@currPath : str
			@linkURL : str
			@size : int
			@modTime : int
	attributes (non-optional):
		str path
		int size
		int modTime
		str linkURL
	attributes (optional):
		-
	methods:
		getters
		@inherited @staticmethod universalEncode, universalDecode
		@override compareToLocal(self, currPath=None, filePath=None, localLinkRUL=None)
			@currPath : str
			@filePath : str
			@localLinkURL : str
			returns bool
		@override encode
		@override @staticmethod decode

class Directory(AbstractFile):
	constructor:
		non-optional arguments:
			@filePath : str
		optional arguments:
			@currPath : str
			@size : int
			@modTime : int
			@mode : int
	attributes (non-optional):
		str path
		int size
		int modTime
		int mode
	attributes (optional):
		-	
	methods:
		getters
		@inherited @staticmethod universalEncode, universalDecode
		@override compareToLocal(self, currPath=None, filePath=None, compareMode=True)
			@currPath : str
			@filePath : str
			@compareMode : bool
			returns bool
		@override encode
		@override @staticmethod decode
