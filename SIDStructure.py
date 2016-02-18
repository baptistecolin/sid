 
import os
import json
import stat
import time ### CHANGE
import datetime ### CHANGE
from file import File ##
from SIDCrypto import *
import base64

crypto = SIDCrypto("orage", algo_cipher = "None")

## TEMP TODO REMOVE
class Protocol():
        def __init__(self, storage, crypto):
                self.crypto = crypto
                self.storage = storage
        def put(self, k, v):
                toWrite = self.crypto.encryptBytes(v)
                self.storage.put(k, toWrite)

        def get(self, k):
                toDecrypt = self.storage.get(k)
                return self.crypto.decryptBytes(toDecrypt)

        def delete(self, k):
                self.storage.delete(k)


protocol_test = Protocol(File('test_dir2/'), crypto)


########  AUXILIARY  ##########################################################

## Recursively lists all files in directory "path" (with included path)
# /!\ Tested on Linux systems only
# @path : str
def listFiles(path, addEntryPath = True, entryPath = ""):
	if path == "": path = "."
	files = []
	l = os.listdir(os.path.join(entryPath, path))
	if not addEntryPath:
		entryPath = path
	for i in l:
		totalPath = os.path.join(path, i) if addEntryPath else i
		if os.path.isdir(os.path.join(entryPath, i)):
			files.append(totalPath)
			files.extend(listFiles(totalPath, True, entryPath))
		if not i.endswith(".sid"): # REMOVE IN LATER VERSIONS (TODO)
			files.append(totalPath)
	return files

def error(msg, errID=-1):
	errIDString = "" if errID == -1 else " (ID:" + errID + ")"
	print("[SID-Structure] ERROR%s: %s" % (errIDString, msg))

def DEBUG(msg):
	print("[SID-Structure] DEBUG: %s" % msg)


########  END AUXILIARY  ######################################################
###############################################################################
########  SID INTERACT   ######################################################

## Returns global SIDKey from "last.sid" in repository
# @protocol : sid.Protocol
def getSIDKey(protocol): ### CHANGE
	try:
		lastSID = json.loads(protocol.get("last.sid").decode("UTF-8"))
	except AssertionError:
		print("[SID-Structure] ERROR: impossible to get key from last.sid: file is corrupt.")
	return lastSID["sidKey"]


########  END SID INTERACT  ###################################################
###############################################################################
########  SID CORE  ###########################################################

## Generate "last.sid" file from version "ver" in directory "path"
# @protocol : sid.Protocol
# @path : str
# @isNew : boolean
def buildSID(protocol, path = "", isNew = False):
	to_upload = []
	dic = {"basics" : {}, "symlinks" : {}, "dirs" : {}}
	if isNew:
		ver = 0
		id_max = 0
		sidKey = "AZERTY" #base64.b64encode(protocol.crypto.globalKeyGenerator()).decode("UTF-8")  ### CHANGE
	else:
		try: ### CHANGE
			last_info = json.loads(protocol.get("last.sid").decode("UTF-8")) ###
		except AssertionError: ### CHANGE
			error("Impossible to read downloaded last.sid: data is corrupt.") ### CHANGE
		ver = last_info["version"] + 1
		sidKey = last_info["sidKey"] ### CHANGE
		id_max = last_info["id_max"]
	dic["sidKey"] = sidKey  ### CHANGE
	dic["version"] = ver
	for f in listFiles(path, False):
		prop = os.lstat(os.path.join(path, f))
		if stat.S_ISLNK(prop.st_mode) != 0:
			ftype = "symlinks"
			linkURL = os.readlink(os.path.join(path, f))
			fhash = None
		elif os.path.isdir(os.path.join(path, f)):
			ftype = "dirs"
			fhash = None
		else:
			ftype = "basics"
			fhash = base64.b64encode(protocol.crypto.hash(os.path.join(path, f), hash_file=True)).decode("UTF-8") ### CHANGE
		if isNew:
			dic[ftype][f] = {"hash" : fhash,
					"size" : prop.st_size,
					"modTime" : prop.st_mtime,
					"mode" : prop.st_mode
					}
			if ftype == "symlinks":
#				dic[ftype][f] = symbolic_link(f, fhash) 
				dic[ftype][f]["linkURL"] = linkURL
			elif ftype == "basics":
				dic[ftype][f]["serverName"] = str(id_max)
#				dic[ftype][f] = basic_file(f, fhash, str(id_max))
				id_max += 1
				to_upload.append(f)
#			elif ftype == "dirs":
#				dic[ftype][f] = directory(f,  fhash)
		else:
			try:
				DEBUG(")
#				if last_info[ftype][f].getHash() == fhash:
				elif last_info[ftype][f]["hash"] == fhash:
					dic[ftype][f] = last_info[ftype][f]					
				else:
					dic[ftype][f] = {"hash" : fhash,
							"size" : prop.st_size,
							"modTime" : prop.st_mtime,
							"mode" : prop.st_mode
							}
					if ftype == "symlinks":
						dic[ftype][f]["linkURL"] = linkURL
#						dic[ftype][f] = symbolic_link(f, fhash) #
					elif ftype == "basics":
						dic[ftype][f]["serverName"] = str(id_max)
#						dic[ftype][f] = basic_file(f, fhash, str(id_max))
						id_max += 1
						to_upload.append(f)
#					elif ftype == "dirs":
#						dic[ftype][f] = directory(f, fhash)
			except KeyError:
				dic[ftype][f] = {"hash" : fhash,
						"size" : prop.st_size,
						"modTime" : prop.st_mtime,
						"mode" : prop.st_mode
						}
				if ftype == "symlinks":
					dic[ftype][f]["linkURL"] = linkURL
#					dic[ftype][f] = symbolic_link(f, fhash) #
				elif ftype == "basics":
					dic[ftype][f]["serverName"] = str(id_max)
#					dic[ftype][f] = basic_file(f, fhash, str(id_max))
					id_max += 1
					to_upload.append(f)
#				elif ftype == "dirs":
#						dic[ftype][f] = directory(f, fhash)
	if to_upload:
		if not isNew:
			# rename previous
			o = open(os.path.join(path, "last.sid"), "rb")
			prevSid = "v" + str(last_info["version"]) + ".sid"
			prev = open(os.path.join(path, prevSid), "wb")
			prev.write(o.read())
			o.close()
			prev.close()
			to_upload.append(prevSid)
		# create new
		dic["id_max"] = id_max
		dic["lastUpdate"] = time.strftime("%d/%m/%Y - %H:%M:%S") ### CHANGE
		o = open(os.path.join(path, "last.sid"), "wb")
		js = json.dumps(dic, o, sort_keys=True, indent=2).encode("UTF-8")
		o.write(js)
		o.close()
		to_upload.append("last.sid")
	return to_upload, dic["basics"]


## Upload directory "path" to update backup
# @protocol : sid.Protocol
# @path : str
def SIDSave(protocol, path = ""):
	to_upload, dic = buildSID(protocol, path)
	for f in to_upload:
		o = open(os.path.join(path, f), "rb")
		try:
			protocol.put(dic[f]["serverName"], o.read())
		except KeyError:
			protocol.put(f.rsplit(os.sep, 1)[-1], o.read())
		o.close()


## Upload directory "path" to create new backup
# @protocol : sid.Protocol
# @path : str
def SIDCreate(protocol, path = ""):
	to_upload, dic = buildSID(protocol, path, True)
	for f in to_upload:
		o = open(os.path.join(path, f), "rb")
		try:
			protocol.put(dic[f]["serverName"], o.read())
#			protocol.put(dic[f].getServerName(), f)
		except KeyError:
			protocol.put("last.sid", o.read())
		o.close()


## Restore directory in "path" from backup (latest version or previous)
# @protocol : sid.Protocol
# @ver : int
# @path : str
def SIDRestore(protocol, path = "", ver = -1, force = False):
	downloaded = []
	if ver < 0:
		try: ### CHANGE
			lastSID = json.loads(protocol.get("last.sid").decode("UTF-8"))
		except AssertionError: ### CHANGE
			print("[SID-Structure] ERROR: impossible to read downloaded last.sid: data is corrupt.")
	else:
		try: ### CHANGE
			lastSID = json.loads(protocol.get("v" + str(ver) + ".sid"))
		except:
			try: ### CHANGE
				lastSID = json.loads(protocol.get("last.sid"))
				if lastSID["version"] != ver:
					raise Exception("Invalid version error.")
			except: ### CHANGE
				error("version %i not found on backend, or is impossible to read (file may be corrupt, retry)." % ver)
				return None

	for d, v in lastSID["dirs"].items():
		os.makedirs(os.path.join(path, d), 0o777, True)
		try:
			os.chmod(os.path.join(path, d), v["mode"])
		except: ""
		try:
			os.utime(os.path.join(path, d), v["modTime"])
		except: ""

	for f, v in lastSID["basics"].items():
		if os.path.exists(os.path.join(path, f)):
			if force:
				fstat = os.lstat(f)
				fhash = protocol.crypto.hash(os.path.join(path, f), hash_file=True) ### CHANGE
				if fstat.st_size != v["size"] or fstat.st_mtime != v["modTime"] or fhash != base64.b64decode(v["hash"].encode("UTF-8")):
					try: ### CHANGE
						fcontent = protocol.get(v["serverName"]).decode("UTF-8")
					except AssertionError: ### CHANGE
						print("[SID-Structure] ATTENTION: impossible to read downloaded file %s: file is corrupt." % f)
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
			print("[SID-DEBUG] -- File found : %s" % f) # REMOVE LATER
		else:
			fhash = None
			try: ### CHANGE
				fcontent = protocol.get(v["serverName"]).decode("UTF-8")
			except AssertionError: ### CHANGE
				print("[SID-Structure] ATTENTION: impossible to read downloaded file %s: file is corrupt." % f)
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
		if os.path.exists(os.path.join(path, l)):
			lstat = os.lstat(l)
			lhash = protocol.crypto.hash(os.path.join(path, l), hash_file=True) ### CHANGE
			if lstat.st_mtime != v["modTime"] or lhash != v["hash"]:
				os.unlink(os.path.join(path, l))
				os.symlink(v["linkURL"], os.path.join(path, l))
				try:
					os.utime(os.path.join(path, l), v["modTime"])
				except: ""
		else:
			os.symlink(v["linkURL"], os.path.join(path, l))
			try:
				os.utime(os.path.join(path, l), v["modTime"])
			except: ""

	return downloaded, lastSID["version"] ### CHANGE


## Get latest version number (from backend last.sid). Returns version if data print was successful, else -1. ### CHANGE
# @protocol : sid.Protocol
def SIDStatus(protocol): ### CHANGE un peu tout
#	try:
	lastSID = json.loads(protocol.get("last.sid").decode("UTF-8"))
#	except AssertionError:
#		print("[SID-Structure] ERROR: impossible to read downloaded last.sid: data is corrupt.")
#		return None
	return str(lastSID["version"]), lastSID["lastUpdate"]


## List files in backend
# @protocol : sid.Protocol
# @detailed : bool
def SIDList(protocol, detailed=False): ### CHANGE un peu tout
	try:
		lastSID = json.loads(protocol.get("last.sid").decode("UTF-8"))
	except AssertionError:
		print("[SID-Structure] ERROR: impossible to read downloaded last.sid: data is corrupt.")
		return None
	flist = []
	for f, v in lastSID["basics"].items():
		if detailed:
			details = {"type" : "FILE",
					"file" : f,
					"size" : v["size"],
					"perms" : v["mode"],
					"lastMod" : str(datetime.datetime.fromtimestamp(v["modTime"]))[:-7]
					}
		else:
			details = {"type" : "FILE",
					"file" : f
					}
		flist.append(details)
	for l, v in lastSID["symlinks"].items():
		if detailed:
			flist.append(l)
			details = {"type" : "LINK",
					"file" : l,
					"size" : v["size"],
					"perms" : v["mode"],
					"lastMod" : str(datetime.datetime.fromtimestamp(v["modTime"]))[:-7]
					}
		else:
			details = {"type" : "FILE",
					"file" : l
					}
		flist.append(details)
	return flist


## Get latest version number (from backend last.sid). Returns version if data print was successful, else -1. ### CHANGE
# @protocol : sid.Protocol
def SIDDelete(protocol): ### CHANGE un peu tout
	deleted = []
	errors = []
	try:
		lastSID = json.loads(protocol.get("last.sid").decode("UTF-8"))
	except AssertionError:
		""
		# TODO : blind removal ?
	for f, v in lastSID["basics"].items():
		try:
			protocol.delete(v["serverName"])
			deleted.append(f)
		except:
			errors.append(f)
	ver = lastSID["version"]
	for i in range(0, ver):
		prevSid = "v" + i + ".sid"
		try:
			protocol.delete(prevSid)
			deleted.append(prevSid)
		except:
			errors.append(prevSid)
	try:
		protocol.delete("last.sid")
		deleted.append("last.sid")
	except:
		errors.append("last.sid")
	return deleted, errors


########  END SID CORE  #######################################################
###############################################################################
###############################################################################
###############################################################################
########  TESTING AREA  #######################################################

if __name__ == '__main__':
	#SIDCreate(protocol_test, "test_dir1/")
	SIDSave(protocol_test, "test_dir1/")
	#SIDRestore(protocol_test, "dir3/")
	print(SIDStatus(protocol_test))
	print(SIDList(protocol_test, True))
	#print(SIDDelete(protocol_test))
	


# fichiers temporaires
	
# ne pas hasher les petits fichiers
# forcer restoration
	
# gros fichiers ?
# grosses arborescences

# rsync : algo qui check si morceaux identiques

