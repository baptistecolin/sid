#coding=utf-8

class server_connection

def put(k, v) :
    #cr�er sur le serveur le fichier envoy�, ou le modifier s'il existe d�j�
    

def get(k) :
    #r�cup�rer le fichier � partir de sa cl� (hash du nom)
    
def delete(k) :
    #supprimer le fichier � partir de sa cl�



def  __contains__(self, key, /) :
    #histoire qu'on puisse utiliser "if key in list"

def __delitem__(self, key, /) :
    #pour que delete self[key] ait un sens

def __eq__(self, value, /) :
    #afin que self==value marche

def __getitem__(x) :
    #x.__getitem__(y)<=>x[y]

def __setitem__(self, key, value, /) :
    #set self[key] to value

def __new__(*args, **kargs) :
    #pour utiliser la syntaxe connection = new connection()
