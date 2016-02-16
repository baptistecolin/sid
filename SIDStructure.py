
# FC: pas très OO pour l'instant !
#     fichiers temporaires ?

import glob
import os.path
import json
import stat
from file import File
#import SIDCrypto
#import sid

#crypto = SIDCrypto("orage", None) # define ??

## Recursively lists all files in directory "path" (with included path)
# /!\ Tested on Linux systems only (incompatible with Windows)
# @path : str
def listFiles(path):
	if path == "": path = "."
	files = []
	l = os.listdir(path + "/")
	for i in l:
		if os.path.isdir(i):
			files.extend(listFiles(i))
		elif not i.endswith(".sid"):
			if path != ".":
				files.append(os.path.join(path, i))
			else:
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
def identityString(path):
	o = open(path, "rb")
	res = o.read()
	o.close()
	return res
	
class cryptoTest():
	def __init__(self):
		self.encrypt = identity
		self.decrypt = identity
		self.decryptString = identityString
		self.hash = identityString
		
crypto = cryptoTest()

# os.readlink(path) : str

### FILE TYPES :
# 0 : basic
# 1 : symbolic link
# 2 : directory
#
## Generate "last.sid" file from version "ver" in directory "path"
# @protocol : server_connection
# @path : str
# @isNew : boolean
def buildSID(protocol, path = "", isNew = False):
	to_upload = []
	dic = {"files" : {}}
	if not isNew:
		o = open(os.path.join(path, "last.sid"), "wb")		
		o.write(protocol.get("last.sid"))
		o.close()
		last_info = json.loads(crypto.decrypt(os.path.join(path, "last.sid")))
		ver = last_info["version"] + 1
		id_max = last_info["id_max"]
	else:
		ver = 0
		id_max = 0
	dic["version"] = ver
	for f in listFiles(path):
		fhash = crypto.hash(f)
		prop = os.lstat(f)
		if stat.S_ISLNK(prop.st_mode) != 0:
			linkURL = os.readlink(f)
			ftype = 1
		elif False: # TODO isDirectory (type 2
			ftype = 2
		else:
			ftype = 0
			linkURL = ""
		if isNew:
			dic["files"][f] = {"serverName" : str(id_max),
					"version" : 0,
					"hash" : fhash,
					"size" : prop.st_size,
					"modTime" : prop.st_mtime,
					"mode" : prop.st_mode,
					"type" : ftype
					}
			id_max += 1
			to_upload.append(f)
		else:
			try:
				if last_info["files"][f]["hash"] == fhash:
					dic["files"][f] = last_info["files"][f]
				else:
					dic["files"][f] = {"serverName" : str(id_max), 								"version" : ver,
							"hash" : fhash,
							"size" : prop.st_size,
							"modTime" : prop.st_mtime,
							"mode" : prop.st_mode,
							"type" : ftype
							}
					id_max += 1
					to_upload.append(f)
			except KeyError:
				dic["files"][f] = {"serverName" : str(id_max), 							"version" : ver,
						"hash" : fhash,
						"size" : prop.st_size,
						"modTime" : prop.st_mtime,
						"mode" : prop.st_mode,
						"type" : ftype
						}
				id_max += 1
				to_upload.append(f)
	if to_upload:
		if not isNew:
			# rename previous
			o = open(os.path.join(path, "last.sid"), "rb")
			prevSid = "v" + str(last_info["version"]) + ".sid"
			prev = open(os.path.join(path, prevSid), "wb")
			prev.write(o.read())
			o.close()
			prev.close()
			to_upload.append(os.path.join(path, prevSid))
		# create new
		dic["id_max"] = id_max
		o = open(os.path.join(path, "last.sid"), "w")
		json.dump(dic, o, sort_keys=True, indent=2)
		o.close()
		js = crypto.encrypt(os.path.join(path, "last.sid"))
		o = open(os.path.join(path, "last.sid"), "wb")
		o.write(js)
		o.close()
		to_upload.append(os.path.join(path, "last.sid"))
	return to_upload, dic["files"]

## Upload directory "path" to update backup
# @protocol : server_connection
# @path : str
def SIDSave(protocol, path = ""):
	to_upload, dic = buildSID(protocol, path)
	for f in to_upload:
		try:
			protocol.put(dic[f]["serverName"], crypto.encrypt(f))
		except KeyError:
			protocol.put("last.sid", crypto.encrypt(os.path.join(path, "last.sid")))

## Upload directory "path" to create new backup
# @protocol : server_connection
# @path : str
def SIDCreate(protocol, path = ""):
	to_upload, dic = buildSID(protocol, path, True)
	for f in to_upload:
		try:
			protocol.put(dic[f]["serverName"], crypto.encrypt(f))
		except KeyError:
			protocol.put("last.sid", crypto.encrypt(os.path.join(path, "last.sid")))
		

## Restore directory in "path" from backup (latest version or previous)
# @protocol : server_connection
# @ver : int
# @path : str
def SIDRestore(protocol, path = "", ver = -1):
	downloaded = []

	if ver < 0:
		lastSID = json.loads(crypto.decryptString(protocol.get("last.sid")))
		o = open(os.path.join(path, "last.sid"), "wb")
		o.write(lastSID) # keep track on local machine
		o.close()
	else:
		lastSID = json.loads(crypto.decryptString(protocol.get("v" + str(ver) + ".sid")))
		o = open(os.path.join(path, "last.sid"), "wb")
		o.write(lastSID) # keep track on local machine
		o.close()
	
	for f, v in lastSID["files"].items():
		fstat = os.lstat(f)
		if fstat.st_size != v["size"] or fstat.st_mtime != v["modTime"]: 
			try:
				fhash = crypto.hash(os.path.join(path, f))
			except IOError:
				fhash = ""
			if fhash != v["hash"]:
				flux = protocol.get(v["serverName"])
				if ftype == 0:
					o = open(os.path.join(path, f), "wb")
					o.write(crypto.decryptString(flux))
					o.close()
				#elif ... ? TODO
				try:
					os.chmod(os.path.join(path, f), v["mode"])
				except: ""
				try:
					os.utime(os.path.join(path, f), v["modTime"])
				except: ""
				downloaded.append(f)
	return downloaded

test_destination_path = 'test_dir2/'	
protocol_test = File(test_destination_path)

SIDCreate(protocol_test, test_destination_path)
#SIDRestore(None, "test_dir")


# status : derniere ver en ligne
# ls pour une ver




