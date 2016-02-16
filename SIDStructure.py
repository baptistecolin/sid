import glob
import os.path
import json
#import SIDCrypto
#import sid

#crypto = SIDCrypto("", "orage", "") # define ??

## Recursively lists all files in directory "path" (with included path)
# /!\ Tested on Linux systems only (incompatible with Windows)
# @path : str
def listFiles(path):
	files = []
	l = glob.glob(path + "/*")
	for i in l:
		print(i)
		if os.path.isdir(i):
			files.extend(listFiles(i))
		elif not i.endswith(".sid"):
			files.append(i)
	return files

print(listFiles(""))

## Generate "last.sid" file from version "ver" in directory "path"
# @path : str
# @isNew : boolean
"""
def buildSID(path, isNew = False):
	to_upload = []
	dic = {}
	dic["files"] = {}
	if not isNew:
		last_info = json.load() #decrypt + download
		ver = last_info["version"] + 1
	else:
		ver = 0
	dic["version"] = ver
	for f in listFiles(path):
		name = f.rsplit("/", 1)[-1]
		fcontent = open(f, "rb").read()
		fhash = crypto.hash(fcontent)
		if isNew:
			dic["files"][f] = {"serverName" : crypto.hash(name, 0), 					"version" : 0,
					"hash" : fhash}
		else:
			try:
				if last_info["files"][f]["hash"] == fhash:
					dic["files"][f] = last_info["files"][f]
				else:
					to_upload.append(f)
					dic["files"][f] = {"serverName" : crypto.hash(name, ver), 								"version" : ver,
							"hash" : fhash}
			except KeyError:
				to_upload.append(f)
				dic["files"][f] = {"serverName" : crypto.hash(name, ver), 							"version" : ver,
						"hash" : fhash}
	if to_upload:
		js = json.dumps(dic)
		js = crypto.encrypt(js)
		open("last.sid", "wb").write(js)
	return to_upload
"""

def buildSID(path = ".", isNew = False):
	to_upload = []
	dic = {}
	dic["files"] = {}
	if not isNew:
		o = open("last.sid", "wb")		
		o.write(sid.protocol.get("last.sid")) # !! nom
		o.close()
		last_info = json.loads(crypto.decrypt("last.sid"))
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
		else:
			try:
				if last_info["files"][f]["hash"] == fhash:
					dic["files"][f] = last_info["files"][f]
				else:
					to_upload.append(f)
					dic["files"][f] = {"serverName" : id_max, 								"version" : ver,
							"hash" : fhash}
					id_max += 1
			except KeyError:
				to_upload.append(f)
				dic["files"][f] = {"serverName" : id_max, 							"version" : ver,
						"hash" : fhash}
				id_max += 1
	if to_upload:
		if not isNew:
			# rename previous
			o = open("last.sid", "rb")
			prevSid = "v" + last_info["version"] + ".sid"
			prev = open(prevSid, "wb")
			prev.write(o.read())
			o.close()
			prev.close()
		# create new
		dic["id_max"] = id_max
		json.dump(dic, "last.sid")
		js = crypto.encrypt("last.sid")
		o = open("last.sid", "wb")
		o.write(js)
		o.close()
		to_upload.append("last.sid")
		to_upload.append(prevSid)
	return to_upload, dic["files"]


def SIDSave(path = "."):
	to_upload, dic = buildSID(path)
	for f in to_upload:
		o = open(f, "rb")
		sid.protocole.put(dic[f]["serverName"], crypto.encrypt(o.read())) # !! nom
		o.close()

def SIDCreate(path = "."):
	to_upload, dic = buildSID(path, True)
	for f in to_upload:
		o = open(f, "rb")
		sid.protocole.put(dic[f]["serverName"], crypto.encrypt(o.read())) # !! nom
		o.close()
		

def SIDRestore(ver = -1, path = "."):
	downloaded = []

	if ver < 0:
		lastSID = json.loads(crypto.decryptString(sid.protocol.get("last.sid")))
		o = open("last.sid", "wb")
		o.write(lastSID) # keep track on local machine
		o.close()
	else:
		lastSID = json.loads(crypto.decryptString(sid.protocol.get("v" + ver + ".sid")))
		o = open("last.sid", "wb")
		o.write(lastSID) # keep track on local machine
		o.close()

	for f, v in lastSID["files"].items():
		o = open(f, "rb")
		fcontent = o.read()
		o.close()
		fhash = crypto.hash(fcontent)
		if fhash != v["hash"]:
			flux = sid.protocol.get(v["serverName"])
			o = open(f, "wb")
			o.write(crypto.decryptString(flux))
			o.close()
			downloaded.append(f)

	return downloaded
	

	





