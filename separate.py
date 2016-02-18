# -*- coding:utf-8 -*-
from imaps import *
from webdav import *
import math
import io

class Separate():

	def __init__(self, store):
		self.MAX = 10
		self.store = store
		print('MAX bytes per block: ', self.MAX)
	
	def getKey(self,k,i):
		return ('%s:%s'%(k,i))

	def get(self, k):
		if k in self.store:
			return self.store.get(k)
		content = []
		i = 0
		while True:
			key = self.getKey(k,i)   # k:i
			if key not in self.store: 
				break
			content.append(self.store.get(key))   # get result sont bytes
			i = i + 1
		if len(content) == 0:
			print("Failed to find the key ", key)
			return None	
		return b''.join(content)
		
	def put(self, k, v):
		n = len(v)
		num = n // self.MAX
		for i in range(num):
			self.store.put(self.getKey(k,i), v[self.MAX * i : self.MAX*(i + 1)])
		if n%self.MAX != 0:
			self.store.put(self.getKey(k,num), v[self.MAX * num: ])
	def delete(self,k):
		j=0
		while True:
			key=self.getKey(k,j)
			if key not in self.store:
				break
			j+=1
			self.store.delete(key)
		if j==0:
			print("There was no file to be deleted!")
		else:
			print("The key was successfully deleted")

if __name__ == '__main__':
	#Test IMAP
	#print("Test imap")
	#IM = Imaps('sid.msip14@gmail.com', 'savefiles', name=b'test')
	#for i in range(5):
		#IM.put(b'toto' + bytes(str(i), 'utf8'), b'blablablablablabla')
		
	#sp = Separate(IM)
	#sp.put(b'totoro', b'blablablablablablablablablablablablablablablablablablablablablablablablablablablablablablablablablablablabla')
	#print(sp.get(b'totoro'))
	#sp.delete(b'totoro')
	#Test Webdav
	print("Test Webdav")
	server=Webdav()
	test=Separate(server)
	test.put('Guru',b'balbalalablabalbalbalbalabalbalbalbbalbalablabalbalbalbalbalablblabalbalablabalbalbalablabalbalbalbalbalbalb')
	print(test.get('Guru'))
	test.delete('Guru')
		
