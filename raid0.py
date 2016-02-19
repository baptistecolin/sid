from file import *
import math

class Raid0():
	def __init__(self,n,stores,weight=[]):
		self.n=n
		assert len(stores)>=2
		self.stores=stores
		self.nbStores=len(stores)
		self.weight=[]
		sum=0
		for k in range(len(weight)):
			sum+=weight[k]
		if len(weight)==len(stores) and sum==1:
			for i in range(len(weight)):
				self.weight.append(math.ceil(weight[i]*(n+1)))
		else:
			print("You haven't entered a correct format for the weights given to the storage capacities. They all have the same weight by default.")
			self.weight=[]
			for i in range(len(stores)):
				self.weight.append(math.ceil((n+1)/len(stores)))
	
	def getKey(self,k,i):
		return '%s-%i'%(k,i)

	def put(self,k,v):
		l=len(v)//self.n
		i=0
		j=0
		putWeight=[]
		for k in range(len(self.weight)):
			putWeight.append(self.weight[k])
		while i<self.n:
			if putWeight[j%self.nbStores]!=0: 	
				self.stores[j%self.nbStores].put(self.getKey(k,i+1),v[i*l:(i+1)*l])
				i+=1
				putWeight[j%self.nbStores]-=1
			j+=1
		while putWeight[j%self.nbStores]==0:
			j+=1 
		self.stores[j%self.nbStores].put(self.getKey(k,self.n+1),v[self.n:])

	def get(self,k):
		content=[]
		i=0
		j=0
		getWeight=[]
		for k in range(len(self.weight)):
			getWeight.append(self.weight[k])
		while i<self.n:
			if getWeight[j%self.nbStores]!=0: 	
				content.append(self.stores[j%self.nbStores].get(self.getKey(k,i+1)))
				i+=1
				getWeight[j%self.nbStores]-=1
			j+=1
		while getWeight[j%self.nbStores]==0:
			j+=1 
		content.append(self.stores[j%self.nbStores].get(self.getKey(k,self.n+1)))
		return b''.join(content)
	
	def delete(self,k):
		i=0
		j=0
		delWeight=[]
		for k in range(len(self.weight)):
			delWeight.append(self.weight[k])
		while i<self.n:
			if delWeight[j%self.nbStores]!=0: 	
				self.stores[j%self.nbStores].delete(self.getKey(k,i+1))
				i+=1
				delWeight[j%self.nbStores]-=1
			j+=1
		while delWeight[j%self.nbStores]==0:
			j+=1 
		self.stores[j%self.nbStores].delete(self.getKey(k,self.n+1))
		
def main():
	raid=Raid0(10,[File('/home/alban/raid0/disk1'),File('/home/alban/raid0/disk2'),File('/home/alban/raid0/disk3')],[0.5,0.5,0])
	raid.put('hello',b'bblablablabalbalbalbalbalbalablabalbalbalbalablabalbalbalablabalbalbalbalabalbalbalbalbalbalab')
	print(raid.get('hello'))
	raid.delete('hello')
if __name__=='__main__':
	main()
