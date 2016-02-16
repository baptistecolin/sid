from server_connection import server_connection
import paramiko
import os


class Ssh(server_connection):
    def __init__(self, login, password, server):
        self.pkey = paramiko.RSAKey.from_private_key_file('rsa.key')
        self.transport=paramiko.Transport((server,22))
        self.transport.connect(username=login, password=password,pkey=self.pkey)
        self.sftp=paramiko.SFTPClient.from_transport(self.transport)


    def put(self,k,v):
        fileServer=self.sftp.open(os.path.join(self.savePath,k),'wb')
        fileServer.close()
        self.sftp.putfo(v, k)
        fileServer.close()

    def get(self, k):
        if self.sftp.file(k,'r'):
            content=''
            size =self.sftp.getfo(k,content)
            return content
        else:
            print("Pas de fichier de ce nom sur le serveur")
            return None

    def delete(self, k):
        if self.sftp.listdir(k):
            self.sftp.remove(k)
            print("le fichier %s  a ete supprime"%k)
        else :
            print("Pas de fichier de ce nom sur le serveur")

