#coding=utf-8

from abc import ABCMeta, abstractmethod

class server_connection(metaclass=ABCMeta):

	@abstractmethod
	def put(self,k, v) :
		pass
    		#cr�er sur le serveur le fichier envoy�, ou le modifier s'il existe d�j�
	    
	@abstractmethod
	def get(self,k) :
		pass
    		#r�cup�rer le fichier � partir de sa cl� (hash du nom)
    	
	@abstractmethod
	def delete(self,k) :
		pass
    		#supprimer le fichier � partir de sa cl�

	def  __contains__(self, key)  :
		if self.get(key) : return True
		else : return False
    		#histoire qu'on puisse utiliser "if key in list"
	
	def __delitem__(self, key) :
		self.delete(key)
    		#pour que delete self[key] ait un sens
	
	@abstractmethod
	def __eq__(self, value) :
    		pass
		#afin que self==value marche
	
	def __getitem__(self,x) :
		self.get(x)
    		#x.__getitem__(y)<=>x[y]
	
	def __setitem__(self, key, value) :
		self.put(key, value)
    		#set self[key] to value
	
	@abstractmethod
	def __new__(self,*args, **kargs) :
		pass
    		#pour utiliser la syntaxe connection = new connection()
 

    


