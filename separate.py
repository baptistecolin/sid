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
    	if k in store:
        	return store.get(k)
        content = []
        i = 0
        while True:
        	key = k + bytes(str(i), 'utf8')		# regular: k + b'0'...
        	if key not in store: 
        		break
        	content.append(store.get(key))			# get result sont bytes
            i+=1
            
        if len(content) == 0:
        	print("Failed to find the clé ", key)
			return None    
		return content	
    
if __name__ == '__main__':
	password = getpass.getpass("enter password: ")
	IM = Imaps('xiangnan.chat@gmail.com', password, name=b'test')
	for i in range(5):
		IM.put(b'toto' + bytes(str(i), utf8), b'blablablablablabla')
	sp = Separate(IM)
	sp.get('toto')
    	