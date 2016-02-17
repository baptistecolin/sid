#! /usr/bin/env python3

import os.path
import os
import json
from pprint import pprint
from SIDCrypto import *

#name of the cach directory
cach_dir = os.environ['HOME'] + '/.sid'

def create_cach(name,crypto,url='',directory_path='',version=0):
    if not os.path.isdir(cach_dir):
       os.mkdir(cach_dir) 
    if os.path.exists(os.path.join(cach_dir,name)):
        print("ERROR: name already taken")
    else:
        save(name,crypto,url,directory_path,version)

def update_cach(name,crypto,version):
#test right password
        (v,url,directory_path) = read_save(name,crypto)
        save(name,crypto,url,directory_path,version)
    

#save a save 
def save(name,crypto,url='',directory_path='',version=0):
    dic = {'version' : version,
        'url' : url,
        'directory_path' : directory_path}
    t = os.path.join(cach_dir, name)
    crypted_json = crypto.encryptBytes(bytes(json.dumps(dic).encode('utf-8')))
    o = open(t,"wb")
    o.write(crypted_json)
    o.close()

def list_saves():
    if not os.path.isdir(cach_dir):
       print("No save on the disk")
    else:
        if len(os.listdir(cach_dir)) == 0:
            print("No save on the disk")
        else:
            for f in os.listdir(cach_dir):
                print(f) 

#get version, url and directory address of a save
def read_save(name,crypto):
    if not os.path.isdir(cach_dir):
       print("No save on the disk")
    else:
        if name not in os.listdir(cach_dir): 
            print("No save with this name")
        else:
            t = cach_dir + '/' + name
            o = open(t,"rb")
            found = o.read() 
            o.close()
            j_dic = json.loads(crypto.decryptBytes(found).decode('utf-8'))
            print(j_dic)
            return (j_dic['version'],j_dic['url'],j_dic['directory_path']) #return (version,url,directory_address) 

#cryptoEx = SIDCrypto("adrien")
#create_cach('save0',cryptoEx,'https://www.google.com/','/home/adrien/Documents/School/Mines/MSI/Cours/msi-p14/dossierTest')
#list_saves()
#read_save('save0',cryptoEx)
#update_cach('save0',cryptoEx,version=1)
#read_save('save0',cryptoEx)
