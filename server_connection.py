#coding=utf-8

from abc import ABCMeta, abstractmethod

class server_connection(object):
	__metaclass__=ABCMeta

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


	@abstractmethod
	def  __contains__(self, key, /) :
		pass
    		#histoire qu'on puisse utiliser "if key in list"
	
	@abstractmethod
	def __delitem__(self, key, /) :
		pass
    		#pour que delete self[key] ait un sens
	
	@abstractmethod
	def __eq__(self, value, /) :
    		pass
		#afin que self==value marche
	
	@abstractmethod
	def __getitem__(self,x) :
		pass
    		#x.__getitem__(y)<=>x[y]
	
	@abstractmethod
	def __setitem__(self, key, value, /) :
		pass
    		#set self[key] to value
	
	@abstractmethod
	def __new__(self,*args, **kargs) :
		pass
    		#pour utiliser la syntaxe connection = new connection()
 

    


