
# -*- coding:utf-8 -*-

from file import *

class Raid1():
	def __init__(self, stores):
		assert len(stores) >= 2
		self.stores = stores
		
	def put(self, k, v):
			for s in self.stores:
				s.put(k, v)
	
	def get(self, k):
		for s in self.stores:
			if s.get(k) != None:
				return s.get(k)
		raise FileNotFoundError('File not found') 

	def delete(self, k):
		for s in self.stores:
			return s.delete(k)
			
def main():
	raid=Raid1([File('disk1'), File('disk2')])
	#raid.put('helloworld',b'blablablabalbalbalbalbalablabalbalbalabalbalbalabalbalablabalbalbalbalablabalbalbalbalbalablabalbalbalbalablabalbalbalbalbalablablablablabalbalblabalbalbalablab')
	a = raid.get('helloworld')
	print(a)
	
if __name__=='__main__':
	main()
