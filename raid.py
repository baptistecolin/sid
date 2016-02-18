# -*- coding:utf-8 -*-

from file import *

class Raid():
	def __init__(self, version=10):
		if int(version)==10 :
			self.version=int(version)

	def getKey(self,k,i):
		return '%s--%s'%(k,i)

	def put(self, k, v):

		disk1=File('/home/alban/raid1/%s-1/'%k)
		disk2=File('/home/alban/raid1/%s-2/'%k)
		disk3=File('/home/alban/raid1/%s-3/'%k)
		disk4=File('/home/alban/raid1/%s-4/'%k)

		n=len(v)
		parts_number=7
		parts = []

		for i in range(parts_number):
			parts.append(v[n // parts_number * i : n // parts_number * (i + 1)])
		parts.append(v[n // parts_number * parts_number:])

		for i in range(parts_number):
			if i%2==0:
				disk1.put(self.getKey(k,i), parts[i])
				disk3.put(self.getKey(k,i), parts[i])
			else :
				disk2.put(self.getKey(k,i), parts[i])
				disk4.put(self.getKey(k,i), parts[i])
def main():
	raid=Raid()
	raid.put('helloworld',b'blablablabalbalbalbalbalablabalbalbalabalbalbalabalbalablabalbalbalbalablabalbalbalbalbalablabalbalbalbalablabalbalbalbalbalablablablablabalbalblabalbalbalablab')
if __name__=='__main__':
	main()
