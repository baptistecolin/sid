# -*- coding:utf-8 -*-

# FC: directory path? error handling?

from server_connection import server_connection
import os

class File(server_connection):
	
	def put(self,k,v):
		fileServer=open(k,'wb')
		fileServer.write(v)
		fileServer.close()
    
	def get(self,k):
		content=open(k,'rb')
		if content:
			return content
		else:
			print("Pas de fichier de ce nom sur le serveur")
			return None
    
	def delete(self,k):
		if os.path.isfile(k):
			os.remove(k)
			print ("le fichier %s  a ete supprime"%k)
		else :
			print("Pas de fichier de ce nom sur le serveur")
#Testing the above functions
def main():
	#server_connection.register(File)
	fileSystem=File()
	test=open("test.txt", 'rb')
	fileSystem.put('1234',test.read())
	print(fileSystem.get('1234').read())
	fileSystem.delete('1234')
