from file import *

class Raid0():
	def __init__(self,n,stores,weight=[]):
		self.n=n
		self.stores=stores
		if len(weight)==len(stores):
			self.weight=weight
		else:
			self.weight=[]
			for i in range(len(stores)):
				self.weight.append(1/len(stores))
	
	def getKey(self,k,i):
		return '%s-%i'%(k,i)

	def put(self,k,v):
		l=len(v)//self.n
		for i in range(self.n):
			self.stores[i%len(self.stores)].put(self.getKey(k,i+1),v[i*l:(i+1)*l])
		self.stores[self.n%len(self.stores)].put(self.getKey(k,self.n+1),v[self.n:])

	def get(self,k):
		content=[]
		for i in range(self.n):
			content.append(self.stores[i%len(self.stores)].get(self.getKey(k,i+1)))
		content.append(self.stores[self.n%len(self.stores)].get(self.getKey(k,self.n+1)))		
		return b''.join(content)
	
	def delete(self,k):
		for i in range(self.n):
			self.stores[i%len(self.stores)].delete(self.getKey(k,i+1))
		self.stores[self.n%len(self.stores)].delete(self.getKey(k,self.n+1))
		
def main():
	raid=Raid0(10,[File('/home/alban/raid0/disk1'),File('/home/alban/raid0/disk2'),File('/home/alban/raid0/disk3')])
	raid.put('hello',b'bblablablabalbalbalbalbalbalablabalbalbalbalablabalbalbalablabalbalbalbalabalbalbalbalbalbalab')
	print(raid.get('hello'))
	raid.delete('hello')
if __name__=='__main__':
	main()
