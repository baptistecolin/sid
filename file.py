#coding=utf-8

from server_connection import server_connection
import os

class file(server_connection):
	
	def __init__(self):
		pass

	def put(self,k,v):
		content=open(k,'wb')
		file=open(v,'rb')
		content.write(file.read())
		content.close()
    
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
			print ("le fichier {} a ete supprime".format(k))
		else :
			print("Pas de fichier de ce nom sur le serveur")
def main():
	file=file()
	file.put(self,1234,'/home/alban/Documents/Python/exemple.txt')
