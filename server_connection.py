#coding=utf-8

# FC: contains un peu violent; à quoi sert new()?

from abc import ABCMeta, abstractmethod

class server_connection(metaclass=ABCMeta):

	@abstractmethod
	def put(self,k, v) :
		pass
    		#créer sur le serveur le fichier envoyé, ou le modifier s'il existe déjà
	    
	@abstractmethod
	def get(self,k) :
		pass
    		#récupérer le fichier à partir de sa clé (hash du nom)
    	
	@abstractmethod
	def delete(self,k) :
		pass
    		#supprimer le fichier à partir de sa clé

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
	'''
	@abstractmethod
	def __new__(self,*args, **kargs) :
		pass
    		#pour utiliser la syntaxe connection = new connection()
 	'''

    


