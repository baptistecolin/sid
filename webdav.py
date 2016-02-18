import httplib2
import os
from server_connection import server_connection

class Webdav(server_connection):
	#Enter 
	def __init__(self,path='',uri='http://10.0.2.15/webdav/',username='sid',pwd='sid'):
		self.server=httplib2.Http()
		self.server.add_credentials(username,pwd)
		self.dest=os.path.join(uri,path)
		print(self.dest)
		self.server.request(self.dest,'MKCOL')

	def put(self,k,v):
		response,content=self.server.request(self.create(self.dest,k),'PUT',body=v)
		self.printStatus("put", response)

	def __contains__(self,key):
		response,content=self.server.request(self.create(self.dest,key),'HEAD')
		return response.status==200

	def get(self,k):
		response,content=self.server.request(self.create(self.dest,k),'GET')
		self.printStatus("get", response)
		if response.status==200:
			return content
		else:
			return None
				
	def create(self,uri,k):
		return os.path.join(uri,k)

	def delete(self,k):
		response,content=self.server.request(self.create(self.dest,k),'DELETE')
		self.printStatus("delete", response)
	
	def printStatus(self,who,response):
		print("%s: %s %s"%(who, response.status,response.reason))	

#Testing the module	
def main():
	web=Webdav('titiBis/')
#	web=Webdav()
	web.get('hello')
	web.put('1234','hello')
	web.get('1234')
	'sample.txt' in web
	web.delete('1234')
if __name__=="__main__":
	main()
			
