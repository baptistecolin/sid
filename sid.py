#!/usr/bin/env python3


########################################################### OPTIONS & ARGUMENTS

import os
import sys
import argparse as ap
import re
import server_connection
import getpass
from urllib.parse import urlparse
from urllib.parse import unquote
from SIDStructure import SIDCreate, SIDRestore, SIDSave, SIDDelete
from SIDCrypto import * 
from cach import * 

parser = ap.ArgumentParser(description="sid command")
parser.set_defaults(op='none')
subs = parser.add_subparsers()

# help sub-command
help = subs.add_parser('help', help='show help')
help.set_defaults(op='help')

help.add_argument('about', nargs='?', choices=['help','create','list','ls','update','status','restore', 'chpass'],
                                  default='help', help='sub-command name')

# list sub-command
slist = subs.add_parser('list', help='list all the saves known on computer')
slist.set_defaults(op='list')

# options and arguments common to almost all: name 
snameurl = ap.ArgumentParser(add_help=False)

snameurl.add_argument('name', type=str, help='Give a save name')
snameurl.add_argument('-p','--password', type=str, help='Give a password')

# create sub-command
scr = subs.add_parser('create', help='create a save', parents=[snameurl])
scr.set_defaults(op='create')

scr.add_argument('directory', type=str, help='specify directory to save')
scr.add_argument('url', type=str, help='specify target url')

# ls sub-command
sls = subs.add_parser('ls', help='list files in a save', parents=[snameurl])
sls.set_defaults(op='ls')

sls.add_argument('-v','--version', type=str, help='specify version')

# delete sub-command
sdel = subs.add_parser('delete', help='delete a save', parents=[snameurl])
sdel.set_defaults(op='delete')

# status sub-command
sstat = subs.add_parser('status', help='print status (last online version) of a save', parents=[snameurl])
sstat.set_defaults(op='status')

# update sub-command
supdate = subs.add_parser('update', help='update a save', parents=[snameurl])
supdate.set_defaults(op='update')

# restore sub-command
srestore = subs.add_parser('restore', help='restore a save')
srestore.set_defaults(op='restore')

srestore.add_argument('-v','--version', type=str, help='specify version')
srestore.add_argument('identifier', type=str, help='specify save name or url')
srestore.add_argument('directory', type=str, help='specify directory to restore')

srestore.add_argument('-nn','--newname', type=str, help='Give a save name')
srestore.add_argument('-p','--password', type=str, help='Give a password')

# chpass sub-command
schpass = subs.add_parser('chpass', help='change the backup\'s password', parents=[snameurl])
schpass.set_defaults(op='chpass')

# parse sub-command, options and arguments
opts = parser.parse_args()

########################################################### FUNCTIONS 

def absPath(path):
        if path[0] == '/':
                return path
        else:
                return os.path.join(os.getcwd(), path)

def getPw():
    if not opts.password == None:
        return opts.password
    else: 
        password = getpass.getpass('sid\'s password : ')
        return password

# Prompt for login and password if they are not known
def getIds(login, password, server):
	if login == None:
		login = input('Login : ')
	if password == None:
		password = getpass.getpass(login + '@' + server + '\'s password : ')
	return (unquote(login), unquote(password))

class Protocol():
        def __init__(self, storage, crypto):
                self.crypto = crypto
                self.storage = storage
        def put(self, k, v):
                print('put in : ' + k)
                toWrite = self.crypto.encryptBytes(v)
                self.storage.put(k, toWrite)

        def get(self, k):
                toDecrypt = self.storage.get(k)
                return self.crypto.decryptBytes(toDecrypt)

        def delete(self, k):
                self.storage.delete(k)

def getStorage(url):
	parseUrl = urlparse(url)
	protocolName = parseUrl.scheme
	backupPath = parseUrl.path
	login = parseUrl.username
	password = parseUrl.password
	server = parseUrl.hostname
	if protocolName == 'file':
		from file import File
		storage = File(backupPath)
	elif protocolName == 'ssh':
		from ssh import Ssh
		print('Sauvegarde ssh dans : ' + backupPath)
		(login, password) = getIds(login, password, server)
		storage = Ssh(backupPath, login, password, server)
	elif protocolName == 'imap' or protocolName == 'imaps':
		from imaps import Imaps
		(login, password) = getIds(login, password, server)
		if backupPath == '':
			storage = Imaps(login, password, server)
		else:
			storage = Imaps(login, password, server, box=backupPath)
	elif protocolName == 'http' or protocolName == 'https':
		from webdav import Webdav
		(login, password) = getIds(login, password, server)
		storage = Webdav('', protocolName+'://'+server, login, password)
	return storage


########################################################### PROGRAM 

if opts.op == 'none':
        opts = parser.parse_args(['help', '--help'])
elif opts.op == 'help':
        parser.parse_args([opts.about, '--help'])
elif opts.op == 'create':
        #crypto
        password = getPw()
        crypto = SIDCrypto(password)
        #protocol
        storage = getStorage(opts.url)
        protocol = Protocol(storage, crypto)
        SIDCreate(protocol, opts.directory)
        create_cach(opts.name, crypto, opts.url, absPath(opts.directory)) 
elif opts.op == 'list':
        list_saves()
elif opts.op == 'ls':
        print('Bonjour')
elif opts.op == 'update':
    password = getPw()
    crypto = SIDCrypto(password)
    try:
        (version,url,directory_path,last_update) = read_save(opts.name,crypto) 
    except (ValueError,AssertionError):
        print('Wrong password')
    else:
        storage = getStorage(url)
        protocol = Protocol(storage, crypto)
        SIDSave(protocol, directory_path)
        update_cach(opts.name, crypto, version+1)
elif opts.op == 'delete':
    password = getPw()
    crypto = SIDCrypto(password)
    try:
        (version,url,directory_path,last_update) = read_save(opts.name,crypto) 
    except (ValueError,AssertionError): 
        print('Wrong password')
    else:
        storage = getStorage(url)
        protocol = Protocol(storage, crypto)
        SIDDelete(protocol)
        cach_delete(opts.name,crypto)
elif opts.op == 'status':
    password = getPw()
    crypto = SIDCrypto(password)
    try:
        (version,url,directory_path,last_update) = read_save(opts.name,crypto) 
    except (ValueError,AssertionError):
        print('Wrong password')
    else:
        print('Name: %s \nURL: %s \nDirectory: %s\n Last_update: %s\n Version: %s' % (opts.name,url,directory_path,last_update,version))
elif opts.op == 'restore':
        password = getPw()
        crypto = SIDCrypto(password)

        # check if url or name is specified
        try:
            parseIdentifier = re.search(r'/', opts.identifier)
            if parseIdentifier == None:
                opts.name = opts.identifier
                (version, url, _, _) = read_save(opts.identifier, crypto)
            else:
                url = opts.identifier
        except (ValueError,AssertionError):
            print('Wrong password')
        else:
            directory_path = opts.directory
            if not(os.path.exists(directory_path) and os.path.isdir(directory_path)):
                os.mkdir(directory_path)
            storage = getStorage(url)
            protocol = Protocol(storage, crypto)
            print('Appel de SIDRestore sur : ' + directory_path)
            #SIDRestore
            if opts.version != None:
                (files_list,restored_version) = SIDRestore(protocol, directory_path,ver=opts.version)
            else:
                (files_list,restored_version) = SIDRestore(protocol, directory_path)
            #Cache
            #if opts.name != None:
            if parseIdentifier == None:
                create_cach(opts.identifier, crypto, url, absPath(opts.directory),version=restored_version,restore=True) 
                print("Restore cached on drive")
            else:
                if opts.newname != None:
                    create_cach(opts.newname, crypto, opts.url, absPath(opts.directory),version=restored_version,restore=True) 
                    print("Restore cached on drive")
                else:
                    print("Please give a name for the restoration") 
            if True:
                print('Sauvegarde : ')
                if opts.identifier == None:
                        print('Nom : ' + opts.identifier)
                        print('Version : ' + str(version))
                print('URl : ' + url)
                print('Directory_path : ' + directory_path)
elif opts.op == 'chpass':
	password = getPw()
	
