# -*- coding:utf-8 -*-

from file import *

class Raid():
	def __init__(self, version=10):
		self.version=version
		
	def getKey(self,k,i):
		return '%s--%s'%(k,i)

	def put(self, k, v):
		if self.version==10:

			disk1=File('/home/alban/raid/%s-1'%k)
			disk2=File('/home/alban/raid/%s-2'%k)
			disk3=File('/home/alban/raid/%s-3'%k)
			disk4=File('/home/alban/raid/%s-4'%k)

			n=len(v)
			parts_number=7
			parts = []

			for i in range(parts_number):
				parts.append(v[n // parts_number * i : n // parts_number * (i + 1)])
			parts.append(v[n // parts_number * parts_number:])

			for i in range(parts_number):
				if i%2==0:
					disk1.put(self.getKey(k,i+1), parts[i])
					disk3.put(self.getKey(k,i+1), parts[i])
				else :
					disk2.put(self.getKey(k,i+1), parts[i])
					disk4.put(self.getKey(k,i+1), parts[i])
		elif self.version==5:

			disk1 = self.store("./" + k + '-1')
			disk2 = self.store("./" + k + '-2')
			disk3 = self.store("./" + k + '-3')

			n=len(v)
			parts = []
			parts.append(v[:n // 2])
			parts.append(v[n // 2:])
			control_sum = b''
			for i in range(0, n // 2):
				control_sum += v[i] ^ v[n // 2 + i]
			parts.append(control_sum)
			if n % 2 != 0: control_sum += v[n]

			disk1.put(self.getKey(k, 1), parts[0])
			disk2.put(self.getKey(k, 2), parts[1])
			disk3.put(self.getKey(k, 3), parts[2])

def main():
	raid=Raid()
	raid.put('helloworld',b'blablablabalbalbalbalbalablabalbalbalabalbalbalabalbalablabalbalbalbalablabalbalbalbalbalablabalbalbalbalablabalbalbalbalbalablablablablabalbalblabalbalbalablab')
if __name__=='__main__':
	main()
