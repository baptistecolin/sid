# -*- coding:utf-8 -*-
from imaps import *
import math
import io

class Separate():

    def __init__(self, store):
        self.MAX = 10
        self.store = store
        print('MAX bytes per block: ', self.MAX)
    
    def get(self, k):
        if k in self.store:
             return self.store.get(k)
        content = []
        i = 0
        while True:
            key = k + bytes(str(i), 'utf8')   # regular: k + b'0'...
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
        if n < self.MAX:
            self.store.put(k, v)
            print('put without separation: ')
            return None
        num = n // self.MAX
        for i in range(num):
            self.store.put(k+ bytes(str(i), 'utf8'), v[self.MAX * i : self.MAX*(i + 1)])
        if n%self.MAX != 0:
            self.store.put(k + bytes(str(num), 'utf8'), v[self.MAX * num: ])
            print('put with separation: ')
    
    def delete(self,k):
        if k in self.store:
             self.store.delete(k)
             return True
        i = 0
        while True:
            key = k + bytes(str(i), 'utf8')   # regular: k + b'0'...
            if key not in self.store: 
                break
            self.store.delete(key)   # get result sont bytes
            i = i + 1
        if i == 0:
            print("Failed to find the key ", key)
            return False   
       
        
        
        
if __name__ == '__main__':
	#password = getpass.getpass("enter password: ")
	IM = Imaps('xiangnan.chat@gmail.com', 'Yxn123456', name=b'test')
	#for i in range(5):
		#IM.put(b'toto' + bytes(str(i), 'utf8'), b'blablablablablabla')
		
	sp = Separate(IM)
	#sp.put(b'totoro', b'test get')
	sp.put(b'totoro', b'blablablablablablablablablablablablablablablablablablablablablablablablablablablablablablablablablablablabla')
	print(sp.get(b'totoro'))
	sp.delete(b'totoro')
    	