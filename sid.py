#!/usr/bin/env python3

# FC: certaines options pas utiles si arguments obligatoires?
# password caché, sans affichage?

########################################################### OPTIONS & ARGUMENTS

import os
import sys
import argparse as ap
import re
import server_connection
import getpass
from file import File
from SIDStructure import SIDCreate, SIDRestore, SIDSave
from SIDCrypto import * 
from cach import * 

parser = ap.ArgumentParser(description="sid command")
parser.set_defaults(op='none')
subs = parser.add_subparsers()

# help sub-command
help = subs.add_parser('help', help='show help')
help.set_defaults(op='help')

help.add_argument('about', nargs='?', choices=['help','create','list','ls','update','dump','status','restore'],
                                  default='help', help='sub-command name')

# list sub-command

slist = subs.add_parser('list', help='list all the saves known on computer')
slist.set_defaults(op='list')

# options and arguments common to almost all: name 
snameurl = ap.ArgumentParser(add_help=False)

snameurl.add_argument('-n','--name', type=str, help='Give a save name')
snameurl.add_argument('-p','--password', type=str, help='Give a password')

# create sub-command
scr = subs.add_parser('create', help='create a save', parents=[snameurl])
scr.set_defaults(op='create')

scr.add_argument('files', nargs='*', help='process these files', type=ap.FileType('rb'), default=[sys.stdin.buffer])
scr.add_argument('-u','--url', type=str, help='specify target url')
scr.add_argument('-d','--directory', type=str, help='specify directory to save')

# setName sub-command
ssn = subs.add_parser('setName', help='set a name to a save at a url', parents=[snameurl])
ssn.set_defaults(op='setName')

ssn.add_argument('-u','--url', type=str, help='specify target url')

# ls sub-command
sls = subs.add_parser('ls', help='list files in a save', parents=[snameurl])
sls.set_defaults(op='ls')

sls.add_argument('-u','--url', type=str, help='specify target url')
sls.add_argument('-v','--version', type=str, help='specify version')

# delete sub-command
sdel = subs.add_parser('delete', help='delete a save', parents=[snameurl])
sdel.set_defaults(op='delete')

sdel.add_argument('-u','--url', type=str, help='specify target url')

# status sub-command
sstat = subs.add_parser('status', help='print status (last online version) of a save', parents=[snameurl])
sstat.set_defaults(op='status')

sstat.add_argument('-u','--url', type=str, help='specify target url')

# update sub-command
supdate = subs.add_parser('update', help='update a save', parents=[snameurl])
supdate.set_defaults(op='update')

# restore sub-command
srestore = subs.add_parser('restore', help='restore a save', parents=[snameurl])
srestore.set_defaults(op='restore')

srestore.add_argument('-u','--url', type=str, help='specify target url')
srestore.add_argument('-v','--version', type=str, help='specify version')
srestore.add_argument('-d','--directory', type=str, help='specify directory to restore')

# parse sub-command, options and arguments
opts = parser.parse_args()

########################################################### FUNCTIONS 

def splitUrl(url): 
        reUrl = re.search(r'^(.*)://(.*)',url) 
        return reUrl.group(1),reUrl.group(2)

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

class Protocol():
        def __init__(self, storage, crypto):
                self.crypto = crypto
                self.storage = storage
        def put(self, k, v):
                toWrite = self.crypto.encryptBytes(v)
                self.storage.put(k, toWrite)

        def get(self, k):
                toDecrypt = self.storage.get(k)
                return self.crypto.decryptBytes(toDecrypt)

        def delete(self, k):
                self.storage.delete(k)

def getStorage(url):
        protocolName, address = splitUrl(url)
        if protocolName == 'file':
                storage = File(address)
        elif protocolName == 'ssh':
                from ssh import Ssh
                # get login, server, path
                parsePath = re.match(r'^(.*)@([^:]*):(.*)$', address)
                login = parsePath.group(1)
                server = parsePath.group(2)
                backupPath = parsePath.group(3)
                print(backupPath)
                password = getpass.getpass(login+'@'+server+'\'s password : ')
                storage = Ssh(backupPath, login, password, server)
        elif protocolName == 'imap' or protocolName == 'imaps':
                from imaps import Imaps
        elif protocolName == 'http' or protocolName == 'https':
                from webdav import Webdav
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
    except ValueError: 
        print('Wrong password')
    else:
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
        try:
            (version,url,directory_path,last_update) = read_save(opts.name,crypto) 
        except ValueError:
            print('Wrong password')
        else:
            print('Name: %s \nURL: %s \nDirectory: %s\n Last_update: %s\n Version: %s' % (opts.name,url,directory_path,last_update,version))
            if opts.name != None:
                (version, url, _, _) = read_save(opts.name, crypto)
            else:
                url = opts.url
            directory_path = opts.directory
            if not(os.path.exists(directory_path) and os.path.isdir(directory_path)):
                os.mkdir(directory_path)
            storage = getStorage(url)
            protocol = Protocol(storage, crypto)
            print('Appel de SIDRestore sur : ' + directory_path)
            SIDRestore(protocol, directory_path)
            if True:
                print('Sauvegarde : ')
                if opts.name != None:
                        print('Nom : ' + opts.name)
                        print('Version : ' + str(version))
                print('URl : ' + url)
                print('Directory_path : ' + directory_path)
