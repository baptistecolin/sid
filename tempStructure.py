
# FC: pas très OO pour l'instant !
#     fichiers temporaires ?

import glob
import os.path #utile ?
import os
import json
import stat
from file import File ##
from SIDCrypto import *
import base64
from FileStructure import *
import datetime
import time

crypto = SIDCrypto.SIDCrypto("orage")

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



## Recursively lists all files in directory "path" (with included path)
# /!\ Tested on Linux systems only (incompatible with Windows)
# @path : str
def listFiles(path, addEntryPath = True, entryPath = ""):
	if path == "": path = "."
	files = []
	l = os.listdir(os.path.join(entryPath, path))
	if not addEntryPath:
		entryPath = path
	for i in l:
		#print("DEBUG : dans listFiles :", i)
		totalPath = os.path.join(path, i) if addEntryPath else i
		if os.path.isdir(os.path.join(entryPath, i)):
			print("DIRECTORY = " + i)
			files.append(totalPath)
			files.extend(listFiles(totalPath, True, entryPath))
		if not i.endswith(".sid"): # REMOVE IN LATER VERSIONS (TODO)
			files.append(totalPath)
	return files

def ERROR(msg, errID=-1):
	errIDString = "" if errID == -1 else " (ID:" + errID + ")"
	print("[SID-Structure] ERROR%s: %s" % (errIDString, str(msg)))

## Generate "last.sid" file in directory "path". 
# isNew is True when the repository is created.
# @protocol : sid.Protocol
# @path : str (chemin relatif)
# @isNew : boolean
def buildSID(protocol, path = "", isNew = False):
	to_upload = []
	dic = {"basics" : {}, "symlinks" : {}, "dirs" : {}}
	if isNew:
		ver = 0
		id_max = 0
	else:
		print("DEBUG : trying to load last_info")
		data = protocol.get("last.sid").decode("UTF-8")
		last_info = json.loads(data, object_hook=AbstractFile.universalDecode) ###
		print("DEBUG : last_info =",last_info)
		print("DEBUG : type de last_info['basics']['file1.txt'] :",type(last_info['basics']['file1.txt']))
		ver = last_info["version"] + 1
		id_max = last_info["id_max"]
	dic["version"] = ver
	for f in listFiles(path, False):
		prop = os.lstat(os.path.join(path, f))
		if stat.S_ISLNK(prop.st_mode) != 0:
			ftype = "symlinks" ###
#			linkURL = os.readlink(os.path.join(path, f)) ###
#			fhash = None ###
		elif os.path.isdir(os.path.join(path, f)):
			ftype = "dirs" ###
#			fhash = None ###
		else:
			ftype = "basics" ###
			fhash = base64.b64encode(crypto.hash(os.path.join(path, f), hash_file=True)).decode("UTF-8") ###
		if isNew:
#			dic[ftype][f] = {"hash" : fhash, ###
#					"size" : prop.st_size, ###
#					"modTime" : prop.st_mtime, ###
#					"mode" : prop.st_mode ###
#					} ###
			if ftype == "symlinks":
				dic[ftype][f] = SymbolicLink(f,currPath=path) ###
#				dic[ftype][f]["linkURL"] = linkURL ###
			elif ftype == "basics":
#				dic[ftype][f]["serverName"] = str(id_max) ###
				#print("DEBUG : trying to write {0} in .sid".format(os.path.join(path,f)))
				dic[ftype][f] = BasicFile(f, str(id_max), currPath=path, hash=fhash)
				id_max += 1
				to_upload.append(f)
			elif ftype == "dirs":
				dic[ftype][f] = Directory(f, currPath=path) ###
		else: ### tout est change...
			if ftype == "symlinks": ###
				dic[ftype][f] = SymbolicLink(f, currPath=path) #
			if ftype == "dirs": ###
				dic[ftype][f] = Directory(f, currPath=path) ###
			if ftype == "basics": ###
				try:
					if last_info[ftype][f].getHash() == fhash:
#					if last_info[ftype][f]["hash"] == fhash:
						dic[ftype][f] = last_info[ftype][f]
					else:
#					dic[ftype][f] = {"hash" : fhash,
#							"size" : prop.st_size,
#							"modTime" : prop.st_mtime,
#							"mode" : prop.st_mode
#							}
						dic[ftype][f] = BasicFile(f, str(id_max), currPath=path, hash=fhash)
#					if ftype == "symlinks":
#						dic[ftype][f]["linkURL"] = linkURL
						
#					elif ftype == "basics":
#						dic[ftype][f]["serverName"] = str(id_max)
#						dic[ftype][f] = basic_file(f, fhash, str(id_max))
						id_max += 1
						to_upload.append(f)
#					elif ftype == "dirs":
#						
				except KeyError:
#				dic[ftype][f] = {"hash" : fhash, ###
#						"size" : prop.st_size, ###
#						"modTime" : prop.st_mtime, ###
#						"mode" : prop.st_mode ###
#						} ###
					dic[ftype][f] = BasicFile(f, str(id_max), currPath=path, hash=fhash) ###
					id_max += 1 ###
					to_upload.append(f) ###
#				if ftype == "symlinks": ###
#					dic[ftype][f]["linkURL"] = linkURL ###
#					dic[ftype][f] = symbolic_link(f, fhash) #
#				elif ftype == "basics": ###
#					dic[ftype][f]["serverName"] = str(id_max) ###
#					dic[ftype][f] = basic_file(f, fhash, str(id_max)) 
#					id_max += 1 ###
#					to_upload.append(f) ###
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
		o = open(os.path.join(path, "last.sid"), "wb")
		print(dic)
		js = json.dumps(dic, o, sort_keys=True, indent=2, default=AbstractFile.universalEncode).encode("UTF-8")
		o.write(js)
		o.close()
		to_upload.append("last.sid")
	return to_upload, dic["basics"]


## Upload directory "path" to update backup
# @protocol : sid.Protocol (?)
# @path : str (chemin relatif)
def SIDSave(protocol, path = ""):
	to_upload, dic = buildSID(protocol, path)
	print("DEBUG : last.sid créé ")
	print("DEBUG : to_upload :",to_upload)
	for f in to_upload:
		o = open(os.path.join(path, f), "rb")
		try:
			print("DEBUG : trying to write {0} on backend".format(f))
#			protocol.put(dic[f]["serverName"], o.read()) ###
			protocol.put(dic[f].getServerName(), o.read()) ###
		except KeyError:
			print("DEBUG : trying to write \".sid\" on backend")
			protocol.put(f.rsplit(os.sep, 1)[-1], o.read())
		o.close()

## Upload directory "path" to create new backup
# @protocol : sid.Protocol (?)
# @path : str (chemin relatif)
def SIDCreate(protocol, path = ""):
	to_upload, dic = buildSID(protocol, path, True)
	print("DEBUG : last.sid créé ")
	print("DEBUG : to_upload :",to_upload)  
	for f in to_upload:
		o = open(os.path.join(path, f), "rb")
		try:
			print("DEBUG : trying to write {0} on backend".format(f))
#			protocol.put(dic[f]["serverName"], o.read()) ###
			protocol.put(dic[f].getServerName(), o.read()) ###
		except KeyError:
			print("DEBUG : trying to write \"last.sid\" on backend")
			protocol.put("last.sid", o.read())
		o.close()
		

## Restore directory in "path" from backup (latest version or previous)
# @protocol : sid.Protocol (?)
# @ver : int
# @path : str
def SIDRestore(protocol, path = "", ver = -1, force = False):
	downloaded = []
	if ver < 0:
		print("DEBUG : trying to load lastSID")
		data = protocol.get("last.sid").decode("UTF-8")
		lastSID = json.loads(data, object_hook = AbstractFile.universalDecode) ###
#		o = open(os.path.join(path, "last.sid"), "wb")
#		o.write(lastSID) # keep track on local machine
#		o.close()
		print("DEBUG : lastSID :", lastSID)
	else:
		try:
			lastSID = json.loads(protocol.get("v" + str(ver) + ".sid"), object_hook = AbstractFile.universalDecode) ###
			print("DEBUG : lastSID :", lastSID)
		except FileNotFoundError:
			print("ERROR in SIDStructure : version %i not found on backend." % ver)
#		o = open(os.path.join(path, "last.sid"), "wb")
#		o.write(lastSID) # keep track on local machine
#		o.close()
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
			if force:
				fstat = os.lstat(f)
				fhash = crypto.hash(os.path.join(path, f), hash_file=True)
				if fstat.st_size != v.getSize() or fstat.st_mtime != v.getModTime or fhash != base64.b64decode(v.getHash().encode("UTF-8")): ###
					fcontent = protocol.get(v.getServerName()).decode("UTF-8") ###
					o = open(os.path.join(path, f), "w")
					o.write(fcontent)
					o.close()
					try:
						os.chmod(os.path.join(path, f), v.getMode()) ###
					except: ""
					try:
						os.utime(os.path.join(path, f), v.getModTime()) ###
					except: ""
					downloaded.append(f)
			print("[SID-DEBUG] -- File found : %s" % f)
		else:
			fhash = None
			fcontent = protocol.get(v.getServerName()).decode("UTF-8") ###
			o = open(os.path.join(path, f), "w")
			o.write(fcontent)
			o.close()
			try:
				os.chmod(os.path.join(path, f), v.getMode()) ###
			except: ""
			try:
				os.utime(os.path.join(path, f), v.getModTime()) ###
			except: ""
			downloaded.append(f)

		"""
		if fstat.st_size != v["size"] or fstat.st_mtime != v["modTime"] or fhash != base64.b64decode(v["hash"].encode("UTF-8")):
			fcontent = protocol.get(v["serverName"])
			o = open(os.path.join(path, f), "w")
			o.write(fcontent)
			o.close()
			try:
				os.chmod(os.path.join(path, f), v.getMode())
			except: ""
			try:
				os.utime(os.path.join(path, f), v.getModTime())
			except: ""
			downloaded.append(f)
		"""

	for l, v in lastSID["symlinks"].items():
		if os.path.exists(os.path.join(path, l)):
			lstat = os.lstat(l)
#			lhash = crypto.hash(os.path.join(path, l), hash_file=True)
			if lstat.st_mtime != v.getModTime() or os.readlin(os.path.join(path, l)) != v.getLinkURL(): ###
				os.unlink(os.path.join(path, l))
				os.symlink(v.getLinkURL(), os.path.join(path, l))
				try:
					os.utime(os.path.join(path, l), getModTime()) ###
				except: ""
		else:
			os.symlink(v.getLinkURL(), os.path.join(path, l)) ###
			try:
				os.utime(os.path.join(path, l), v.getModTime())
			except: ""

	return downloaded

## Get latest version number (from backend last.sid)
# @protocol : sid.Protocol
def SIDStatus(protocol):
	lastSID = json.loads(protocol.get("last.sid").decode("UTF-8"), object_hook = AbstractFile.universalDecode) ###
	return str(lastSID["version"]), lastSID["lastUpdate"]

## List files in backend
# @protocol : sid.Protocol
def SIDList(protocol, detailed=False): ### CHANGE un peu tout
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
					"lastMod" : str(datetime.datetime.fromtimestamp(v.getModTime()))[:-7]
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
					"lastMod" : str(datetime.datetime.fromtimestamp(v.getModTime()))[:-7]
					}
		else:
			details = {"type" : "FILE",
					"file" : l
					}
		flist.append(details)
	return flist

## Tests
cible = input('emplacement de la sauvegarde ? ')
if cible == '':
	cible = 'dir_test/save2'
#source = input('dossier à sauvegarder ? ')
#if source == '':
#	source = 'dir_test/aCopier'
protocol_test = Protocol(File(cible), crypto)
#test = input('Que voulez-vous tester ?')
'''if test == '':
	test = 'restore'
if test == 'build':
	print("DEBUG : début de la création de last.sid") 
	buildSID(protocol_test, source, True)
elif test == 'create':
	SIDCreate(protocol_test, source)
elif test == 'save':
	SIDSave(protocol_test, source)
elif test == 'restore':
	SIDRestore(protocol_test, target)'''
#cible = input('emplacement de la sauvegarde ? ')
#SIDCreate(protocol_test, source)
#if cible == '':
#	cible = 'dir_test/save'
#protocol_test = Protocol(File(cible), crypto)
#target = input('où restaurer ? ')
#if target == '':
#	target = 'dir_test/res2'
print(SIDList(protocol_test, detailed=True))


## controle d'integrite sur les fichiers
