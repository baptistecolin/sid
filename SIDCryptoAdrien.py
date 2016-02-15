#!/usr/bin/env python3

########################################################### OPTIONS & ARGUMENTS

import sys
import argparse as ap
import re

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

slist.add_argument('--url', type=str, help='specify target url')

# options and arguments common to almost all: name and url 
snameurl = ap.ArgumentParser(add_help=False)

snameurl.add_argument('--name', type=str, help='Give a save name')
snameurl.add_argument('--url', type=str, help='specify target url')

# create sub-command
scr = subs.add_parser('create', help='create a save', parents=[snameurl])
scr.set_defaults(op='create')

scr.add_argument('files', nargs='*', help='process these files', type=ap.FileType('rb'), default=[sys.stdin.buffer])

# ls sub-command
sls = subs.add_parser('ls', help='list files in a save', parents=[snameurl])
sls.set_defaults(op='ls')

# update sub-command
supdate = subs.add_parser('update', help='update a save', parents=[snameurl])
supdate.set_defaults(op='update')

supdate.add_argument('files', nargs='*', help='process these files', type=ap.FileType('rb'), default=[sys.stdin.buffer])

# dump sub-command
sdump = subs.add_parser('dump', help='dump a save', parents=[snameurl])
sdump.set_defaults(op='dump')

# status sub-command
sstatus = subs.add_parser('status', help='status of a save', parents=[snameurl])
sstatus.set_defaults(op='status')

# restore sub-command
srestore = subs.add_parser('restore', help='restore a save', parents=[snameurl])
srestore.set_defaults(op='restore')

# parse sub-command, options and arguments
opts = parser.parse_args()

def getProtocol(url):
    reUrl = re.search(r'^(.*):',url)
    return (reUrl.group(1))

if opts.op == 'none':
	opts = parser.parse_args(['help', '--help'])
elif opts.op == 'help':
	parser.parse_args([opts.about, '--help'])
elif opts.op == 'create':
    print('bonjour')	
    for file in opts.files:
        print('coucou')
elif opts.op == 'list':
    print('coucou')
elif opts.op == 'ls':
    print('coucou')
elif opts.op == 'update':
    protocol = getProtocol(opts.url) 
elif opts.op == 'dump':
    print('coucou')
elif opts.op == 'update':
    print('coucou')
elif opts.op == 'restore':
    print('coucou')

