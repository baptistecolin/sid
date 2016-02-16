from server_connection import server_connection
import os


class Ssh(server_connection):
    def put(self, k, v):
        """fileServer=open(k,'wb')"""

    # fileServer.write(v)
    # fileServer.close()

    def get(self, k):
        """content=open(k,'rb')"""

    # if content:
    #	return content
    # else:
    #	print("Pas de fichier de ce nom sur le serveur")
    #	return None

    def delete(self, k):
        """if os.path.isfile(k):"""
        #	os.remove(k)
        #	print ("le fichier %s  a ete supprime"%k)
        # else :
        #	print("Pas de fichier de ce nom sur le serveur")
