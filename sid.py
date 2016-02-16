#!/usr/bin/env python3

# FC: certaines options pas utiles si arguments obligatoires?
# password caché, sans affichage?

########################################################### OPTIONS & ARGUMENTS

import os
import sys
import argparse as ap
import re
import server_connection
from file import File
from SIDStructure import SIDCreate

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

# parse sub-command, options and arguments
opts = parser.parse_args()

########################################################### FUNCTIONS 

def getProtocol(): 
    reUrl = re.search(r'^(.*)://(.*)',opts.url) 
    return reUrl.group(1),reUrl.group(2)

def getPwd():
    return input('Password?')

########################################################### PROGRAM 

if opts.op == 'none':
    opts = parser.parse_args(['help', '--help'])
elif opts.op == 'help':
    parser.parse_args([opts.about, '--help'])
elif opts.op == 'create':
    print('Création du dépôt + ' + opts.name + ' dans : ' + opts.url)
    protocolName,adress = getProtocol()
    if protocolName == 'file':
        SIDCreate(opts.directory)
        for file in opts.files:
            aEcrire = file.read()
            if not os.path.isdir(adress):
                os.mkdir(adress)
            protocol = File(adress)
            protocol.put(file.name, aEcrire)
#    elif protocol == 'http' or protocol == 'https':
#    elif protocol == 'imap' or protocol == 'imaps':
#    print('Dépot créé')
elif opts.op == 'list':
    pwd = getPwd()
    protocol,address = getProtocol()
    print(address)
    print(protocol)
    print(pwd)	
elif opts.op == 'ls':
    pwd = getPwd()
    protocol,address = getProtocol()
    print(pwd)	
elif opts.op == 'update':
    pwd = getPwd()
    protocol,address = getProtocol()
    print(pwd)	
elif opts.op == 'dump':
    pwd = getPwd()
    protocol,address = getProtocol()
    print(pwd)	
elif opts.op == 'update':
    pwd = getPwd()
    protocol,address = getProtocol()
    print(pwd)	
elif opts.op == 'restore':
    pwd = getPwd()
    protocol,address = getProtocol()
    print(pwd)	

