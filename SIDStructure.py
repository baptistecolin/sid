
# FC: pas très OO pour l'instant !
#     fichiers temporaires ?

import glob
import os.path #utile ?
import os
import json
import stat
from file import File
import SIDCrypto
#import sid

crypto = SIDCrypto("orage", None) # define ??

# @path : chemin depuis le repertoire sauvegarde
class files:
	def __init__(self, path, hash = ""):
		self.path = path
		if "":
			self.hash = hash
		else: #empty string
			self.hash = crypto.hash(path, h_file = True)
		prop = os.lstat(f)
		self.size = prop.st_size,
		self.modTime = prop.st_mtime,
	def getHash(self):
		return self.hash

class basic_file(files):
	def __init__(self, path, hash = "", serverName):
		files.__init__(self, path, hash)
		prop = os.lstat(f)
		self.mode = prop.st_mode
		self.serverName = serverName
	def getServerName(self):
		return self.serverName

class symbolic_link(files):
	def __init__(self, path, hash = ""):
		files.__init__(self, path, hash)
			self.linkURL = os.readlink(path)

class directory(files):
	def __init__(self, path, hash = ""):
		files.__init__(self, path, hash)
		prop = os.lstat(f)
		self.mode = prop.st_mode


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

## Generate "last.sid" file from version "ver" in directory "path"
# @protocol : server_connection (?)
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
		fhash = crypto.hash(f, hash_file=True)
#		prop = os.lstat(f)
		if stat.S_ISLNK(prop.st_mode) != 0:
			ftype = "symlinks"
#			dic["symlinks"] = symbolic_link(os.join(path, f), str(id_max)) #### ??
#			linkURL = os.readlink(f)
		elif os.path.isdir(os.path.join(path, f)):
			ftype = "dirs"
		else:
			ftype = "basics"
		if isNew:
#			dic[ftype][f] = {"hash" : fhash,
#					"size" : prop.st_size,
#					"modTime" : prop.st_mtime,
#					"mode" : prop.st_mode
#					}
			if ftype == "symlinks":
				dic[ftype][f] = symbolic_link(f, fhash) #
#				dic[ftype][f]["linkURL"] = linkURL
			elif ftype == "basics":
#				dic[ftype][f]["serverName"] : str(id_max)
				dic[ftype][f] = basic_file(f, fhash, str(id_max))
				id_max += 1
				to_upload.append(f)
			elif ftype == "dirs":
				dic[ftype][f] = directory(f,  fhash)
		else:
			try:
				if last_info[ftype][f].getHash() == fhash:
					dic[ftype][f] = last_info[ftype][f]
				else:
#					dic[ftype][f] = {"hash" : fhash,
#							"size" : prop.st_size,
#							"modTime" : prop.st_mtime,
#							"mode" : prop.st_mode
#							}
					if ftype == "symlinks":
#						dic[ftype][f]["linkURL"] = linkURL
						dic[ftype][f] = symbolic_link(f, fhash) #
					elif ftype == "basics":
#						dic[ftype][f]["serverName"] : str(id_max)
						dic[ftype][f] = basic_file(f, fhash, str(id_max))
						id_max += 1
						to_upload.append(f)
					elif ftype == "dirs":
						dic[ftype][f] = directory(f, fhash)
			except KeyError:
#				dic[ftype][f] = {"hash" : fhash,
#						"size" : prop.st_size,
#						"modTime" : prop.st_mtime,
#						"mode" : prop.st_mode
#						}
				if ftype == "symlinks":
#					dic[ftype][f]["linkURL"] = linkURL
					dic[ftype][f] = symbolic_link(f, fhash) #
				elif ftype == "basics":
#					dic[ftype][f]["serverName"] : str(id_max)
					dic[ftype][f] = basic_file(f, fhash, str(id_max))
					id_max += 1
					to_upload.append(f)
				elif ftype == "dirs":
						dic[ftype][f] = directory(f, fhash)
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
#		js = crypto.encrypt(os.path.join(path, "last.sid"))
#		o = open(os.path.join(path, "last.sid"), "wb")
#		o.write(js)
#		o.close()
		to_upload.append(os.path.join(path, "last.sid"))
	return to_upload, dic["basics"]


## Upload directory "path" to update backup
# @protocol : server_connection
# @path : str
def SIDSave(protocol, path = ""):
	to_upload, dic = buildSID(protocol, path)
	for f in to_upload:
		try:
			protocol.put(dic[f].getServerName(), f)
		except KeyError:
			protocol.put(rsplit(os.sep, 1)[-1], f)

## Upload directory "path" to create new backup
# @protocol : server_connection
# @path : str
def SIDCreate(protocol, path = ""):
	to_upload, dic = buildSID(protocol, path, True)
	for f in to_upload:
		try:
			protocol.put(dic[f].getServerName(), f)
		except KeyError:
			protocol.put("last.sid", f)
		

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

## List files
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


protocol_test = File('test_dir2/')
#SIDCreate(protocol_test, "test_dir1/")
#SIDSave(protocol_test, "test_dir1/")
#SIDRestore(protocol_test, "dir3/")





