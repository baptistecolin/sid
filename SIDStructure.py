
# FC: pas très OO pour l'instant !
#     fichiers temporaires ?

import glob
import os.path
import json
import stat
from file import File ##
from SIDCrypto import *
import base64

## TEMP TODO remove
class Protocol():
	def __init__(self, storage, crypto):
		self.crypto = crypto
		self.storage = storage
	# backupFile : file's name
	# toBackup : file's name
	def put(self, k, v):
		toWrite = self.crypto.encryptBytes(v)
		self.storage.put(k, toWrite)

	def get(self, k):
		toDecrypt = self.storage.get(k)
		print("type(toDecrypt): %s" % type(toDecrypt))
		m = self.crypto.decryptBytes(toDecrypt)
		print("type(m): %s" % type(m))
		return m


crypto = SIDCrypto("orage")

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
		if not i.endswith(".sid"):
			if path != ".":
				files.append(os.path.join(path, i))
			else:
				files.append(i)
	return files

"""
## Pour les tests
# @path : str
def identity(path):
	o = open(path, 'rb')
	res = o.read()
	o.close()
	return res
	
# @x : str
def identityString(path):
	o = open(path, "r")
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
"""

#def: binToHex():

### FILE TYPES :
# 0 : basic
# 1 : symbolic link
# 2 : directory
## Generate "last.sid" file from version "ver" in directory "path"
# @protocol : server_connection
# @path : str
# @isNew : boolean
def buildSID(protocol, path = "", isNew = False):
	to_upload = []
	dic = {"basics" : {}, "symlinks" : {}, "dirs" : {}}
	if not isNew:
		last_info = json.loads(protocol.get("last.sid")) ##
		ver = last_info["version"] + 1
		id_max = last_info["id_max"]
	else:
		ver = 0
		id_max = 0
	dic["version"] = ver
	for f in listFiles(path):
		fhash = base64.b64encode(crypto.hash(f, hash_file=True)).decode("ASCII")  ## HASH_PROBLEMS
		prop = os.lstat(f)
		if stat.S_ISLNK(prop.st_mode) != 0:
			ftype = "symlinks"
			linkURL = os.readlink(f)
		elif os.path.isdir(os.path.join(path, f)):
			ftype = "dirs"
		else:
			ftype = "basics"
		if isNew:
			dic[ftype][f] = {"hash" : fhash,
					"size" : prop.st_size,
					"modTime" : prop.st_mtime,
					"mode" : prop.st_mode
					}
			if ftype == "symlinks":
				dic[ftype][f]["linkURL"] = linkURL
			elif ftype == "basics":
				dic[ftype][f]["serverName"] = str(id_max)
				id_max += 1
				to_upload.append(f)
		else:
			try:
				if last_info[ftype][f]["hash"] == fhash:
					dic[ftype][f] = last_info[ftype][f]
				else:
					dic[ftype][f] = {"hash" : fhash,
							"size" : prop.st_size,
							"modTime" : prop.st_mtime,
							"mode" : prop.st_mode
							}
					if ftype == "symlinks":
						dic[ftype][f]["linkURL"] = linkURL
					elif ftype == "basics":
						dic[ftype][f]["serverName"] = str(id_max)
						id_max += 1
						to_upload.append(f)
			except KeyError:
				dic[ftype][f] = {"hash" : fhash,
						"size" : prop.st_size,
						"modTime" : prop.st_mtime,
						"mode" : prop.st_mode
						}
				if ftype == "symlinks":
					dic[ftype][f]["linkURL"] = linkURL
				elif ftype == "basics":
					dic[ftype][f]["serverName"] = str(id_max)
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
		o = open(os.path.join(path, "last.sid"), "wb")
		print(dic)
		js = json.dumps(dic, o, sort_keys=True, indent=2).encode("ASCII")
		o.write(js)
		o.close()
		to_upload.append(os.path.join(path, "last.sid"))
	return to_upload, dic["basics"]


## Upload directory "path" to update backup
# @protocol : server_connection
# @path : str
def SIDSave(protocol, path = ""):
	to_upload, dic = buildSID(protocol, path)
	for f in to_upload:
		o = open(f, "rb").read()
		try:
			protocol.put(dic[f]["serverName"], o.read())
		except KeyError:
			protocol.put(rsplit(os.sep, 1)[-1], o.read())
		o.close()

## Upload directory "path" to create new backup
# @protocol : server_connection
# @path : str
def SIDCreate(protocol, path = ""):
	to_upload, dic = buildSID(protocol, path, True)
	for f in to_upload:
		o = open(f, "rb")
		try:
			protocol.put(dic[f]["serverName"], o.read())
		except KeyError:
			protocol.put("last.sid", o.read())
		o.close()
		

## Restore directory in "path" from backup (latest version or previous)
# @protocol : server_connection
# @ver : int
# @path : str
def SIDRestore(protocol, path = "", ver = -1):
	downloaded = []
	if ver < 0:
		lastSID = json.loads(protocol.get("last.sid"))
#		o = open(os.path.join(path, "last.sid"), "wb")
#		o.write(lastSID) # keep track on local machine
#		o.close()
	else:
		try:
			lastSID = json.loads(protocol.get("v" + str(ver) + ".sid"))
		except:
			print("ERROR in SIDStructure : version %i not found on backend." % ver)
#		o = open(os.path.join(path, "last.sid"), "wb")
#		o.write(lastSID) # keep track on local machine
#		o.close()
	
	for d, v in lastSID["dirs"].items():
		os.makedirs(os.path.join(path, d), 0o777, True)
		try:
			os.chmod(os.path.join(path, d), v["mode"])
		except: ""
		try:
			os.utime(os.path.join(path, d), v["modTime"])
		except: ""

	for f, v in lastSID["basics"].items():
		try:
			fhash = crypto.hash(os.path.join(path, f), h_file=True)
			fstat = os.lstat(f)
		except IOError:
			fhash = ""
		if fstat.st_size != v["size"] or fstat.st_mtime != v["modTime"] or fhash != v["hash"]:
			fcontent = protocol.get(v["serverName"])
			o = open(os.path.join(path, f), "w")
			o.write(fcontent)
			o.close()
			try:
				os.chmod(os.path.join(path, f), v["mode"])
			except: ""
			try:
				os.utime(os.path.join(path, f), v["modTime"])
			except: ""
			downloaded.append(f)

	for l, v in lastSID["symlinks"].items():
		try:
			lhash = crypto.hash(os.path.join(path, l), h_file=True)
			lstat = os.lstat(l)
			if lstat.st_mtime != v["modTime"] or lhash != v["hash"]:
				os.unlink(os.path.join(path, l))
				os.symlink(v["linkURL"], os.path.join(path, l))
				try:
					os.utime(os.path.join(path, l), v["modTime"])
				except: ""
		except IOError:
			os.symlink(v["linkURL"], os.path.join(path, l))
			try:
				os.utime(os.path.join(path, l), v["modTime"])
			except: ""

	return downloaded

## Get latest version number (from backend last.sid)
# @protocol : server_connection
def SIDStatus(protocol):
	lastSID = json.loads(protocol.get("last.sid"))
	print("Latest backend version: v%i" % lastSID["version"])
	return lastSID["version"]

## List files in backend
# @protocol : server_connection
def SIDList(details=False):
	lastSID = json.loads(protocol.get("last.sid"))
	flist = []
	for f in lastSID["basics"]:
		flist.append(f)
		details = [f["size"], readMode(f["mode"]), datetime.datetime.fromtimestamp(f["modTime"])]
		print("[FILE] " + f)
	for l in lastSID["symlinks"]:
		flist.append(l)
		details = [f["size"], readMode(f["mode"]), datetime.datetime.fromtimestamp(f["modTime"])]
		print("[LINK] " + f)
	return flist


protocol_test = Protocol(File('test_dir2/'), crypto)

#SIDCreate(protocol_test, "test_dir1/")
SIDSave(protocol_test, "test_dir1/")
#SIDRestore(protocol_test, "dir3/")





