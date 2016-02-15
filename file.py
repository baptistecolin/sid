#coding=utf-8

class file(server_connection):
    
    def put(self,k,v) :
        content = open(k,'wb')
        content.write(v)
        content.close()
    
    def get(self,k) :
        content=open(k,'rb')
        if content : return content
        else :
            print("Pas de fichier de ce nom sur le serveur")
            return None
    
    def delete(self,k) :
        import os
        if os.path.isfile(k) :
            os.remove(k)
            print ("le fichier {} a été supprimé".format(k))
        else :
            print("Pas de fichier de ce nom sur le serveur")

