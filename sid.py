#!/usr/bin/env python3

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

slist = subs.add_parser('list', help='list all the saves')
slist.set_defaults(op='list')

slist.add_argument('-u','--url', type=str, help='specify target url')

# options and arguments common to almost all: name and url 
snameurl = ap.ArgumentParser(add_help=False)

snameurl.add_argument('-n','--name', type=str, help='Give a save name')
snameurl.add_argument('-u','--url', type=str, help='specify target url')

# create sub-command
scr = subs.add_parser('create', help='create a save', parents=[snameurl])
scr.set_defaults(op='create')

scr.add_argument('-d', type=str, help='specify a directory')
scr.add_argument('files', nargs='*', help='process these files', type=ap.FileType('rb'), default=[sys.stdin.buffer])

# ls sub-command
sls = subs.add_parser('ls', help='list files in a save', parents=[snameurl])
sls.set_defaults(op='ls')

# update sub-command
supdate = subs.add_parser('update', help='update a save', parents=[snameurl])
supdate.set_defaults(op='update')

supdate.add_argument('files', nargs='*', help='process these files', type=ap.FileType('rb'), default=[sys.stdin.buffer])

# remove sub-command
sremove = subs.add_parser('remove', help='remove a save', parents=[snameurl])
sremove.set_defaults(op='remove')

# status sub-command
sstatus = subs.add_parser('status', help='status of a save', parents=[snameurl])
sstatus.set_defaults(op='status')

# restore sub-command
srestore = subs.add_parser('restore', help='restore a save', parents=[snameurl])
srestore.set_defaults(op='restore')

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
#    pwd = getPwd()
#    protocol = getProtocol()
    protocol,adress = getProtocol()
#    adress
#    print(pwd)
#    print(protocol)
    SIDCreate('aCopier/')
#    for file in opts.files:
#        aEcrire = file.read()
#        File.put(File, os.path.join(chemin,file.name), aEcrire)
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

