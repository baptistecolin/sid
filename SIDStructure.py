 
import os
import json
import stat
import time
import datetime
from FileStructure import *
from file import File ## REMOVE AFTER TESTS
from SIDCrypto import * ## REMOVE AFTER TESTS
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
			files.extend(listFiles(totalPath, True, entryPath))
		files.append(totalPath)
	return files

def mtimeToTuple(modTime):
	modTime = str(modTime)
	part1, part2 = modTime.split(".")
	return (int(part1), int(part2))


def ERROR(msg, errID=-1):
	errIDString = "" if errID == -1 else " (ID:" + errID + ")"
	print("[SID-Structure] ERROR%s: %s" % (errIDString, str(msg)))

def ATTENTION(msg):
	print("[SID-Structure] ATTENTION: %s" % str(msg))

def DEBUG(msg):
	print("[SID-Structure] DEBUG: %s" % str(msg))


########  END AUXILIARY  ######################################################
###############################################################################
########  SID INTERACT   ######################################################

## Returns global SIDKey from "last.sid" in repository
# @protocol : sid.Protocol
def getSIDKey(protocol): ### CHANGE
	try:
		lastSID = json.loads(protocol.get("last.sid").decode("UTF-8"))
	except AssertionError:
		ERROR("Impossible to get key from last.sid: file is corrupt.")
	return lastSID["sidKey"]


########  END SID INTERACT  ###################################################
###############################################################################
########  SID CORE  ###########################################################

## Generate "last.sid" file in directory "path". 
# isNew is True when the repository is created.
# @protocol : sid.Protocol
# @path : str (chemin relatif)
# @isNew : boolean
def buildSID(protocol, path = "", isNew = False):
	to_upload = []
	sids = {}
	sldChanged = False
	dic = {"basics" : {}, "symlinks" : {}, "dirs" : {}}
	if isNew:
		ver = 0
		id_max = 0
		sidKey = "AZERTY" #base64.b64encode(protocol.crypto.globalKeyGenerator()).decode("UTF-8") ## TODO ?
		sidHoles = []
	else:
		try:
			data = protocol.get("last.sid").decode("UTF-8")
			last_info = json.loads(data, object_hook=AbstractFile.universalDecode)
		except AssertionError:
			ERROR("Impossible to read downloaded last.sid: data is corrupt.")
		ver = last_info["version"] + 1
		sidKey = last_info["sidKey"]
		id_max = last_info["id_max"]
		sidHoles = last_info["sidHoles"]
	dic["sidKey"] = sidKey
	dic["version"] = ver
	dic["sidHoles"] = sidHoles
	for f in listFiles(path, False):
		prop = os.lstat(os.path.join(path, f))
		if stat.S_ISLNK(prop.st_mode) != 0:
			ftype = "symlinks"
			try:
				if isNew or os.readlin(os.path.join(path, f)) != last_info[ftype][f].getLinkURL() or os.lstat(os.path.join(path, f)).st_mtime != last_info[ftype][f].getModTime():
					dic[ftype][f] = SymbolicLink(f, currPath=path)
					sldChanged = True
				else:
					dic[ftype][f] = last_info[ftype][f]
			except KeyError:
				dic[ftype][f] = SymbolicLink(f, currPath=path)
				sldChanged = True
		elif os.path.isdir(os.path.join(path, f)):
			ftype = "dirs"
			dic[ftype][f] = Directory(f, currPath=path)
			try:
				if isNew or os.lstat(os.path.join(path, f)).st_mtime != last_info[ftype][f].getModTime():
					dic[ftype][f] = Directory(f, currPath=path)
					sldChanged = True
				else:
					dic[ftype][f] = last_info[ftype][f]
			except KeyError:
				dic[ftype][f] = Directory(f, currPath=path)
				sldChanged = True
		else: #ftype = "basics"
			ftype = "basics"
			fhash = base64.b64encode(protocol.crypto.hash(os.path.join(path, f), hash_file=True)).decode("UTF-8")
			if isNew:
				dic[ftype][f] = BasicFile(f, str(id_max), currPath=path, hash=fhash)
				id_max += 1
				to_upload.append(f)
			else:
				try:
					if last_info[ftype][f].getHash() == fhash:
						dic[ftype][f] = last_info[ftype][f]
					else:
						dic[ftype][f] = BasicFile(f, str(id_max), currPath=path, hash=fhash)
						id_max += 1
						to_upload.append(f)
				except KeyError:
					dic[ftype][f] = BasicFile(f, str(id_max), currPath=path, hash=fhash)
					id_max += 1
					to_upload.append(f)

	if to_upload or sldChanged:
		if not isNew:
			# rename previous
			prevSid = "v" + str(last_info["version"]) + ".sid"
			sids[prevSid] = data.encode('UTF-8')
		# create new
		dic["id_max"] = id_max
		dic["lastUpdate"] = time.strftime("%d/%m/%Y - %H:%M:%S")
		js = json.dumps(dic, sort_keys=True, indent=2, default=AbstractFile.universalEncode).encode("UTF-8")
		sids["last.sid"] = js
	return to_upload, dic["basics"], sids


## Upload directory "path" to update backup
# @protocol : sid.Protocol
# @path : str (chemin relatif)
def SIDSave(protocol, path = ""):
	to_upload, dic, sids = buildSID(protocol, path)
	for f in to_upload:
		o = open(os.path.join(path, f), "rb")
		protocol.put(dic[f].getServerName(), o.read())
		o.close()
	for k, v in sids.items():
		protocol.put(k, v)


## Upload directory "path" to create new backup
# @protocol : sid.Protocol
# @path : str (chemin relatif)
def SIDCreate(protocol, path = ""):
	to_upload, dic, sids = buildSID(protocol, path, True)
	for f in to_upload:
		o = open(os.path.join(path, f), "rb")
		protocol.put(dic[f].getServerName(), o.read())
		o.close()
	protocol.put("last.sid", sids["last.sid"])


## Restore directory in "path" from backup (latest version or previous)
# @protocol : sid.Protocol
# @ver : int
# @path : str (chemin relatif)
def SIDRestore(protocol, path = "", ver = -1, force = False):
	downloaded = []
	if ver < 0:
		try:
			lastSID = json.loads(protocol.get("last.sid").decode("UTF-8"), object_hook = AbstractFile.universalDecode)
		except AssertionError:
			ERROR("Impossible to read downloaded last.sid: data is corrupt.")
	else:
		try:
			lastSID = json.loads(protocol.get("v" + str(ver) + ".sid"), object_hook = AbstractFile.universalDecode)
		except:
			try:
				lastSID = json.loads(protocol.get("last.sid"), object_hook = AbstractFile.universalDecode)
				if lastSID["version"] != ver:
					raise Exception("Invalid version ERROR.")
			except:
				ERROR("version %i not found on backend, or is impossible to read (data may be corrupt, retry)." % ver)
				return None

	for d, v in lastSID["dirs"].items():
		os.makedirs(os.path.join(path, d), 0o777, True)
		try:
			os.chmod(os.path.join(path, d), v.getMode())
		except: ""
		try:
			os.utime(os.path.join(path, d), v.getModTime())
		except: ""

	for f, v in lastSID["basics"].items():
		if os.path.exists(os.path.join(path, f)):
			fstat = os.lstat(os.path.join(path, f))
			fhash = protocol.crypto.hash(os.path.join(path, f), hash_file=True)
			if force:
				if fstat.st_size != v.getSize() or fstat.st_mtime != v.getModTime or fhash != base64.b64decode(v.getHash().encode("UTF-8")):
					try:
						fcontent = protocol.get(v.getServerName()).decode("UTF-8")
						o = open(os.path.join(path, f), "w")
						o.write(fcontent)
						o.close()
						downloaded.append(f)
						os.chmod(os.path.join(path, f), v.getMode())
						os.utime(os.path.join(path, f), mtimeToTuple(v.getModTime()))
					except AssertionError:
						ATTENTION("Impossible to read downloaded file %s: file is corrupt." % f)
		else:
			try:
				fcontent = protocol.get(v.getServerName()).decode("UTF-8")
				o = open(os.path.join(path, f), "w")
				o.write(fcontent)
				o.close()
				downloaded.append(f)
				os.chmod(os.path.join(path, f), v.getMode())
				print(v.getModTime(), mtimeToTuple(v.getModTime()))
				os.utime(os.path.join(path, f), mtimeToTuple(v.getModTime()))
			except AssertionError:
				ATTENTION("Impossible to read downloaded file %s: file is corrupt." % f)

	for l, v in lastSID["symlinks"].items():
		if os.path.exists(os.path.join(path, l)):
			lstat = os.lstat(l)
			if lstat.st_mtime != v.getModTime() or os.readlin(os.path.join(path, l)) != v.getLinkURL():
				os.unlink(os.path.join(path, l))
				os.symlink(v.getLinkURL(), os.path.join(path, l))
				try:
					os.utime(os.path.join(path, l), getModTime())
				except: ""
		else:
			os.symlink(v.getLinkURL(), os.path.join(path, l))
			try:
				os.utime(os.path.join(path, l), v.getModTime())
			except: ""

	return downloaded, lastSID["version"]


## Get latest version number (from backend last.sid). Returns version if data print was successful, else -1.
# @protocol : sid.Protocol
def SIDStatus(protocol):
	try:
		lastSID = json.loads(protocol.get("last.sid").decode("UTF-8"), object_hook = AbstractFile.universalDecode)
	except AssertionError:
		ERROR("impossible to read downloaded last.sid: data is corrupt.")
		return None
	return str(lastSID["version"]), lastSID["lastUpdate"]


## List files in backend
# @protocol : sid.Protocol
# @detailed : bool
def SIDList(protocol, detailed=False):
	try:
		lastSID = json.loads(protocol.get("last.sid").decode("UTF-8"), object_hook = AbstractFile.universalDecode)
	except AssertionError:
		ERROR("impossible to read downloaded last.sid: data is corrupt.")
		return None
	flist = []
	for f, v in lastSID["basics"].items():
		if detailed:
			details = {"type" : "FILE",
					"file" : f,
					"size" : v.getSize(),
					"perms" : v.getMode(),
					"lastMod" : str(datetime.datetime.fromtimestamp(v.getModTime())).split(".")[0]
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
					"size" : v.getSize(),
					"perms" : v.getMode(),
					"lastMod" : str(datetime.datetime.fromtimestamp(v.getModTime())).split(".")[0]
					}
		else:
			details = {"type" : "FILE",
					"file" : l
					}
		flist.append(details)
	return flist


## Delete the entire backend repository. For single-version deletion, see 'SIDRemove'
# @protocol : sid.Protocol
def SIDDelete(protocol):
	deleted = []
	errors = []
	try:
		lastSID = json.loads(protocol.get("last.sid").decode("UTF-8"), object_hook = AbstractFile.universalDecode)
	except AssertionError:
		ERROR("Impossible to read data from last.sid: data is corrupt.")
		return None
	for f, v in lastSID["basics"].items():
		try:
			protocol.delete(v.getServerName())
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


## Delete a version backup on the backend repository, with garbage collector at work
## Returns the number of deletions and errors
# @protocol : sid.Protocol
# @version : int
def SIDRemove(protocol, ver=-1):
	deleted = 0
	errors = 0
	try:
		lastSID = json.loads(protocol.get("last.sid").decode("UTF-8"), object_hook = AbstractFile.universalDecode)
		if ver < -1 or ver > lastSID["version"]:
			ERROR("Version %i not found on backend. Latest version is: %i" % (ver, lastSID["version"]))
		toRemove = [True for i in range(0, lastSID["id_max"])]
		holeList = lastSID["sidHoles"]
		for i in range(0, lastSID["version"]):
			if i != ver:
				prevSID = json.loads(protocol.get("v" + str(i) + ".sid").decode("UTF-8"), object_hook = AbstractFile.universalDecode)
				for f, v in prevSID["basics"].items():
					toRemove[int(v.getServerName())] = False
				if ver == lastSID["version"] and i = ver - 1:
					sidSave = prevSID
		if ver != lastSID["version"]:
			for f, v in lastSID["basics"].items():
				toRemove[int(v.getServerName())] = False
		for v in holeList:
			toRemove[v] = False
		for i in range(0, lastSID["id_max"]):
			if toRemove[i]:
				try:
					protocol.delete(str(i))
					holeList.append(i)
					deleted += 1
				except:
					errors += 1
		try:
			protocol.delete("last.sid" if ver == lastSID["version"] else "v" + str(ver) + ".sid")
		except:
			ERROR("Could not delete corresponding .sid distant file.")
		if ver == lastSID["version"]:
			sidSave["sidHoles"] = holeList
			protocol.put("last.sid", json.dumps(sidSave, sort_keys=True, indent=2, default=AbstractFile.universalEncode).encode("UTF-8"))
			try:
				protocol.delete("v" + str(ver-1) + ".sid")
			except: "" # do nothing
	except AssertionError:
		ERROR("Impossible to read data from .sid files on backend: data is corrupt.")
		return None
	return deleted, errors


########  END SID CORE  #######################################################
###############################################################################
###############################################################################
###############################################################################
########  TESTING AREA  #######################################################

if __name__ == '__main__':
	SIDCreate(protocol_test, "test_dir1/")
	#SIDSave(protocol_test, "test_dir1/")
	#print(SIDStatus(protocol_test))
	#print("LIST :",SIDList(protocol_test, True))
	#SIDRestore(protocol_test, "dir3/")
	#print(SIDDelete(protocol_test))
	#print(SIDRemove(protocol_test, 0))
	

# grosses arborescences
# rsync : algo qui check si morceaux identiques

