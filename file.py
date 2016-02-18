# -*- coding:utf-8 -*-

# FC: directory path? error handling?

from server_connection import server_connection
import os

class File(server_connection):
	
	def __init__(self,path):
		self.savePath=path
		if not os.path.exists(path):
			os.makedirs(path)
	
	def put(self,k,v):
		fileServer=open(os.path.join(self.savePath,k),'wb')
		fileServer.write(v)
		fileServer.close()
	 
	def get(self,k):
		try:
			return open(os.path.join(self.savePath,k),'rb').read()
		except FileNotFoundError:
			print('No such files in', self.savePath)

	def delete(self,k):
		for root, dirs, files in os.walk(self.savePath):
			if k in files:
				os.remove(os.path.join(root,k))
				print ("The file %s was deleted!"%k)
#Testing the above functions
def main():
	fileSystem=File('/home/alban/Documents/test/')
	test=open("test.txt", 'rb')
	fileSystem.put('1234',test.read())
	print(fileSystem.get('12345'))
	fileSystem.delete('1234')
if __name__=='__main__':
	main()
