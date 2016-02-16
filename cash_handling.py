#! /usr/bin/env python3

import os.path
import os

#name of the cash directory
cash_dir = 'sidCash'

#create a save file with info
def create_credentials_file(name,url,directory_address):
    if not os.path.isdir(cash_dir):
       os.mkdir(cash_dir) 
    if name in os.listdir(cash_dir): 
         print("There is already a save with this name")
    version = 0
    t = cash_dir + '/' + name
    o = open(t,"w")

#storage on 3 lines: version number, server url, directory_address
    o.write(str(version) + "\n")
    o.write(url + "\n")
    o.write(directory_address)
    o.close()

def list_saves():
    if not os.path.isdir(cash_dir):
       print("No save on the disk")
    else:
       for f in os.listdir(cash_dir):
            print(f) 

#get version, url and directory address of a save
def read_save(name):
    if not os.path.isdir(cash_dir):
       print("No save on the disk")
    else:
        if name not in os.listdir(cash_dir): 
            print("No save with this name")
        else:
            t = cash_dir + '/' + name
            o = open(t,"r")
            lines = o.read().splitlines()
            o.close()
            #print(lines)
            return (lines[0],lines[1],lines[2]) #return (version,url,directory_address) 

#update save version in the cash
def update_version(name):
    if not os.path.isdir(cash_dir):
       print("No save on the disk")
    else:
        if name not in os.listdir(cash_dir): 
            print("No save with this name")
        else:
            (version,url,directory_address) = read_save(name)              
            version = int(version) + 1
            t = cash_dir + '/' + name
            o = open(t,"w")
            o.write(str(version) + "\n")
            o.write(url + "\n")
            o.write(directory_address)
            o.close() 

#create_credentials_file('save0','https://www.google.com/','/home/adrien/Documents/School/Mines/MSI/Cours/dossierTest')
#list_saves()
#read_save('save0')
#update_version('save0')
#read_save('save0')
