import glob
import os.path
import json
#import SIDCrypto
#import sid

#crypto = SIDCrypto("", "", "") # define ??

## Recursively lists all files in directory "path" (with included path)
# @path : str
def listFiles(path):
	files = []
	l = glob.glob(path + "/*")
	for i in l:
		if os.path.isdir(i):
			files.extend(listFiles(i))
		elif i != (path + "/last.sid"):
			files.append(i)
	return files

print(listFiles("."))

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

def buildSID(path, isNew = False):
	to_upload = []
	dic = {}
	dic["files"] = {}
	if not isNew:
		last_info = json.load() #decrypt + download
		ver = last_info["version"] + 1
		id_max = last_info["id_max"]
	else:
		ver = 0
		id_max = 0
	dic["version"] = ver
	for f in listFiles(path):
		name = f.rsplit("\\", 1)[-1]
		fcontent = open(f, "rb").read()
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
		dic["id_max"] = id_max
		js = json.dumps(dic)
		js = crypto.encrypt(js)
		open("last.sid", "wb").write(js)
	return to_upload
	 



