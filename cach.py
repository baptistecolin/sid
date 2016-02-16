#! /usr/bin/env python3

import os.path
import os
import json
from pprint import pprint

#name of the cach directory
cach_dir = os.environ['HOME'] + '/.sid'

#save a save 
def save(name,url='',directory_path='',version=0):
    if not os.path.isdir(cach_dir):
       os.mkdir(cach_dir) 
    if name in os.listdir(cach_dir): 
        (v,url,directory_path) = read_save(name)
    dic = {'version' : version,
        'url' : url,
        'directory_path' : directory_path}
    t = cach_dir + '/' + name
    o = open(t,"w")
    json.dump(dic,o,sort_keys = True,indent=2)
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
def read_save(name):
    if not os.path.isdir(cach_dir):
       print("No save on the disk")
    else:
        if name not in os.listdir(cach_dir): 
            print("No save with this name")
        else:
            t = cach_dir + '/' + name
            o = open(t,"r")
            j_dic = json.loads(o.read())
            o.close()
            #print(j_dic)
            return (j_dic['version'],j_dic['url'],j_dic['directory_path']) #return (version,url,directory_address) 

#save('save0','https://www.google.com/','/home/adrien/Documents/School/Mines/MSI/Cours/dossierTest')
#list_saves()
#read_save('save0')
#save('save0',version=1)
#read_save('save0')
