import glob
import os.path
import json
#import SIDCrypto
import sid

#crypto = SIDCrypto("", "orage", "") # define ??

## Recursively lists all files in directory "path" (with included path)
# /!\ Tested on Linux systems only (incompatible with Windows)
# @path : str
def listFiles(path):
	if path == 0: path = "."
	files = []
	l = glob.glob(path + "/*")
	for i in l:
		print(i)
		if os.path.isdir(i):
			files.extend(listFiles(i))
		elif not i.endswith(".sid"):
			files.append(i)
	return files

## Pour les tests
# @path : str
def identity(path):
	o = open(path, 'rb')
	res = o.read()
	o.close()
	return res
	
# @x : str
def identityString(x):
	return x
	
class cryptoTest():
	def __init__(self):
		self.encrypt = identity
		self.decrypt = identity
		self.decryptString = identityString
		self.hash = identityString
		
crypto = cryptoTest()
	
## Generate "last.sid" file from version "ver" in directory "path"
# @path : str
# @isNew : boolean
def buildSID(path = "", isNew = False):
	to_upload = []
	dic = {}
	dic["files"] = {}
	if not isNew:
		o = open(path + "last.sid", "wb")		
		o.write(sid.protocol.get("last.sid")) # !! nom
		o.close()
		last_info = json.loads(crypto.decrypt(path + "last.sid"))
		ver = last_info["version"] + 1
		id_max = last_info["id_max"]
	else:
		ver = 0
		id_max = 0
	dic["version"] = ver
	for f in listFiles(path):
#		name = f.rsplit("/", 1)[-1]
		o = open(f, "rb")
		fcontent = o.read()
		o.close()
		fhash = crypto.hash(fcontent)
		if isNew:
			dic["files"][f] = {"serverName" : id_max,
					"version" : 0,
					"hash" : fhash}
			id_max += 1
			to_upload.append(f)
		else:
			try:
				if last_info["files"][f]["hash"] == fhash:
					dic["files"][f] = last_info["files"][f]
				else:
					dic["files"][f] = {"serverName" : id_max, 								"version" : ver,
							"hash" : fhash}
					id_max += 1
					to_upload.append(f)
			except KeyError:
				dic["files"][f] = {"serverName" : id_max, 							"version" : ver,
						"hash" : fhash}
				id_max += 1
				to_upload.append(f)
	if to_upload:
		if not isNew:
			# rename previous
			o = open(path + "last.sid", "rb")
			prevSid = "v" + str(last_info["version"]) + ".sid"
			prev = open(path + prevSid, "wb")
			prev.write(o.read())
			o.close()
			prev.close()
			to_upload.append(path + prevSid)
		# create new
		dic["id_max"] = id_max
		o = open(path + "last.sid", "wb")
		json.dump(dic, o)
		o.close()
		js = crypto.encrypt("last.sid")
		o = open(path + "last.sid", "wb")
		o.write(js)
		o.close()
		to_upload.append(path + "last.sid")
	return to_upload, dic["files"]


## Upload directory "path" to update backup
# @path : str
def SIDSave(path = ""):
	to_upload, dic = buildSID(path)
	for f in to_upload:
		o = open(f, "rb")
		sid.protocole.put(dic[f]["serverName"], crypto.encrypt(o.read())) # !! nom
		o.close()

## Upload directory "path" to create new backup
# @path : str
def SIDCreate(path = ""):
	to_upload, dic = buildSID(path, True)
	for f in to_upload:
		o = open(f, "rb")
		sid.protocole.put(dic[f]["serverName"], crypto.encrypt(o.read())) # !! nom
		o.close()
		

## Restore directory in "path" from backup (latest version or previous)
# @ver : int
# @path : str
def SIDRestore(ver = -1, path = ""):
	downloaded = []

	if ver < 0:
		lastSID = json.loads(crypto.decryptString(sid.protocol.get("last.sid")))
		o = open(path + "last.sid", "wb")
		o.write(lastSID) # keep track on local machine
		o.close()
	else:
		lastSID = json.loads(crypto.decryptString(sid.protocol.get("v" + str(ver) + ".sid")))
		o = open(path + "last.sid", "wb")
		o.write(lastSID) # keep track on local machine
		o.close()

	for f, v in lastSID["files"].items():
		try:
			o = open(path + f, "rb")
			fcontent = o.read()
			o.close()
			fhash = crypto.hash(fcontent)
		except IOError:
			fhash = ""
		if fhash != v["hash"]:
			flux = sid.protocol.get(v["serverName"])
			o = open(path + f, "wb")
			o.write(crypto.decryptString(flux))
			o.close()
			downloaded.append(f)

	return downloaded
	

	


# status : derniere ver en ligne
# ls pour une ver




