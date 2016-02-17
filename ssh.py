from server_connection import server_connection
import paramiko
import io
import os
import getpass


class Ssh(server_connection):
    def __init__(self, path, login, password, server):
        self.savePath=path
        self.transport=paramiko.Transport((server,22))
        self.transport.connect(username=login, password=password)
        self.sftp=paramiko.SFTPClient.from_transport(self.transport)
        print("connexion au serveur " + server +" à travers le serveur SFTP " + str(self.sftp) + " réussie")


    def put(self,k,v):
        fileServer=self.sftp.open(os.path.join(self.savePath,k),'wb')
        print("ouverture du fichier "+k+" sur le serveur distant")
        fileServer.close()
        input=io.BytesIO(v)
        self.sftp.putfo(input, os.path.join(self.savePath,k))
        print("Écriture du fichier "+k+" réussie")

    def get(self, k):
        if self.sftp.file(k,'r'):
            output=io.BytesIO()
            size =self.sftp.getfo(k,output)
            print("Récupération du fichier "+k+" réussie")
            return output.getvalue()
        else:
            print("Pas de fichier de ce nom sur le serveur")
            return None

    def delete(self, k):
        if k in self.sftp.listdir():
            self.sftp.remove(os.path.join(self.savePath,k))
            print("le fichier %s  a ete supprime"%k)
        else :
            print("Pas de fichier de ce nom sur le serveur")

    def changePath(self, path):
        self.savePath=path

def main():
    server=input('Serveur :')
    login=input('Login :')
    password=getpass.getpass('Password :')
    fileSystem = Ssh(".",login,password,server)
    assert fileSystem is not None
    test = open('test.txt','rb')
    fileSystem.put('test.txt',test.read())
    content=fileSystem.get('test.txt')
    print(content)
    fileSystem.delete('test.txt')

if __name__=='__main__':
    main()
