#coding=utf-8

class server_connection():

	def __init__(self):
		print("Abstract class : Cannot create instance")		
		self.__del__()
	
	def put(self,k, v) :
		pass
    		#créer sur le serveur le fichier envoyé, ou le modifier s'il existe déjà
	    
	def get(self,k) :
		pass
    		#récupérer le fichier à partir de sa clé (hash du nom)
    	
	def delete(self,k) :
		pass
    		#supprimer le fichier à partir de sa clé

	def  __contains__(self, key)  :
		if self.get(key)!=None : return True
		else : return False
    		#histoire qu'on puisse utiliser "if key in list"
	
	def __delitem__(self, key) :
		self.delete(key)
    		#pour que delete self[key] ait un sens
	def __eq__(self, value) :
    		pass
		#afin que self==value marche
	def __getitem__(self,x) :
		self.get(x)
    		#x.__getitem__(y)<=>x[y]
	
	def __setitem__(self, key, value) :
		self.put(key, value)
    		#set self[key] to value
#Testing abstract type
def main():
	s=server_connection()

if __name__=='__main__':
	main()
