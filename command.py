#! /usr/bin/env python3

########################################################### OPTIONS & ARGUMENTS

import sys
import argparse as ap

parser = ap.ArgumentParser(description="crypto stuff")
parser.set_defaults(op='none')
subs = parser.add_subparsers()

# help sub-command
help = subs.add_parser('help', help='show help')
help.set_defaults(op='help')

help.add_argument('about', nargs='?', choices=['help','digest','enc','dec'],
				  default='help', help='sub-command name')

# digest sub-command
sd = subs.add_parser('digest', help='compute a cryptographic digest')
sd.set_defaults(op='digest')

sd.add_argument('--algo', type=str, choices=['sha256','sha1','md5','sha512'],
				default='sha256', help='use this digest algorithm')
# shortcuts
sd.add_argument('--sha256', dest='algo', action='store_const', const='sha256',
				help='use SHA256 digest')
sd.add_argument('--sha1', dest='algo', action='store_const', const='sha1',
				help='use SHA1 digest')
sd.add_argument('--md5', dest='algo', action='store_const', const='md5',
				help='use MD5 digest')
# n arguments
sd.add_argument('files', nargs='*', help='process these files',
				type=ap.FileType('rb'), default=[sys.stdin.buffer])

# options and arguments common to encoding & decoding
encdec = ap.ArgumentParser(add_help=False)
encdec.add_argument('--algo', type=str, choices=['aes','blowfish'],
					default='aes', help='use this encryption algorithm')
encdec.add_argument('--mode', type=str, choices=['cbc','ecb','ofb','cfb','ctr'],
					default='cbc', help='use this block cipher mode')
encdec.add_argument('--password', type=str, default=None,
					help='encryption password')
encdec.add_argument('--hash', type=str, choices=['sha256','sha1','md5'],
					default=None, help='hash algorithm for integrity check')
# shortcuts
encdec.add_argument('--aes', dest='algo', action='store_const', const='aes',
					help='use the AES algorithm')
encdec.add_argument('--cbc', dest='mode', action='store_const', const='cbc',
					help='use the CBC block cipher mode')
# two arguments
encdec.add_argument('infile', nargs='?', help='input file to process',
					type=ap.FileType('rb'), default=sys.stdin.buffer)
encdec.add_argument('outfile', nargs='?', help='output file to write',
					type=ap.FileType('wb'), default=sys.stdout.buffer)

# enc sub-command
senc = subs.add_parser('enc', help='encode a file', parents=[encdec])
senc.set_defaults(op='enc')

# dec-sub-command
sdec = subs.add_parser('dec', help='decode a file', parents=[encdec])
sdec.set_defaults(op='dec')

# parse sub-command, options and arguments
opts = parser.parse_args()

##################################################################### FUNCTIONS

from Crypto.Hash import *

# return a hash algorithm
def hash(algo):
	ALGOS = { 'sha256':SHA256, 'sha1':SHA, 'md5':MD5, 'sha512':SHA512 }
	return ALGOS[algo] if algo in ALGOS else None

# compute file digest
def digest(file, hash=SHA256):
	h = hash.new()
	# yuk, python is missing something...
	while True:
		buf = file.read(65536)
		if not buf: break
		h.update(buf)
	file.close()
	return h.hexdigest()

from Crypto.Cipher import *

# interpret options for algorithm, mode, padding & iv
def crypto(opts):
	from Crypto.Cipher import blockalgo as ba
	MODES = { 'cbc':ba.MODE_CBC, 'cfb':ba.MODE_CFB, 'ofb':ba.MODE_OFB,
			  'ctr':ba.MODE_CTR, 'ecb':ba.MODE_ECB }
	ALGOS = { 'aes':AES, 'blowfish':Blowfish }
	assert opts.algo in ALGOS, "unexpected cipher %s" % opt.algo
	assert opts.mode in MODES, "unexpected mode %s" % opt.mode
	algo, mode = ALGOS[opts.algo], MODES[opts.mode]
	pad = opts.mode in [ 'cbc', 'ecb', 'ofb' ]
	iv = opts.mode in [ 'cbc', 'ofb', 'cfb' ]
	#print("algo=%s mode=%s pad=%s iv=%s" % (algo, mode, pad, iv),
	#      file=sys.stderr)
	return (algo, mode, pad, iv)

# return key/iv/salt
def kis(password, salt=None, iv=None, rand=None,
		keylen=16, ivlen=16, saltlen=8, hash=SHA512):
	#print("keylen=%s" % keylen, file=sys.stderr)
	#print("salt=%s iv=%s keylen=%d ivlen=%d saltlen=%d" %
	#		  (salt, iv, keylen, ivlen, saltlen), file=sys.stderr)
	# note: if rand is doubtful, should combine with the password
	if salt is None and saltlen > 0:
		salt = rand.read(saltlen)
	else:
		assert salt is None or len(salt) == saltlen
	if iv is None and ivlen > 0:
		iv = rand.read(ivlen)
	else:
		assert iv is None or len(iv) == ivlen
	assert hash.digest_size >= keylen, "hash large enough for key derivation"
	h = hash.new()
	h.update(password)
	h.update(salt)
	key = h.digest()[:keylen]
	#print("kis: key=%s iv=%s salt=%s" % (key, iv, salt), file=sys.stderr)
	# yuk:-)
	if rand is not None:
		return (key, iv, salt)
	else:
		return key

# encode infile to outfile
# file format is:
#  - 8-byte salt
#  - block-size iv if needed by mode
#  - encrypt(infile + hash(infile) + padding)
def enc(infile, outfile, algo, mode, key, iv, pad, hash=None):
	#print("enc: key=%s iv=%s pad=%s" % (key, iv, pad), file=sys.stderr)
	cipher = algo.new(key, mode, iv)
	clair = infile.read()
	# append digest *before* encrypting
	if hash is not None:
		h = hash.new()
		h.update(clair)
		clair += h.digest()
	# pad if needed
	if pad:
		padlen = algo.block_size - (len(clair) % algo.block_size)
		if padlen == 0:
			padlen = algo.block_size
		clair += bytearray((chr(padlen) * padlen).encode('ASCII'))
	chiffre = cipher.encrypt(clair)
	#print("clair=%d chiffre=%d" % (len(clair), len(chiffre)), file=sys.stderr)
	outfile.write(chiffre)
	outfile.close()

# decode infile contents to outfile
def dec(infile, outfile, algo, mode, key, iv, pad, hash=None):
	#print("dec: key=%s iv=%s" % (key, iv), file=sys.stderr)
	cipher = algo.new(key, mode, iv)
	chiffre = infile.read()
	clair = cipher.decrypt(chiffre)
	#print("clair: %s" % clair, file=sys.stderr)
	if pad:
		padlen = clair[-1]
		assert 1 <= padlen <= algo.block_size, \
			"invalid padding length %d" % padlen
		assert clair[-padlen:] == (chr(padlen) * padlen).encode('ASCII'), \
			"invalid padding"
		clair = clair[:-padlen]
	if hash is not None:
		# split digest & check
		clair, hv = clair[:-hash.digest_size], clair[-hash.digest_size:]
		h = hash.new()
		h.update(clair)
		hn = h.digest()
		assert hn == hv, \
			"unexpected hash %s, expecting %s" % (hn, hv)
		#print("# hash checked", file=sys.stderr)
	outfile.write(clair)
	outfile.close()

######################################################################## ACTION

if opts.op == 'none':
	opts = parser.parse_args(['help', '--help'])
elif opts.op == 'help':
	parser.parse_args([opts.about, '--help'])
elif opts.op == 'digest':
	algo = hash(opts.algo)
	for file in opts.files:
		print("%s(%s): %s" % (opts.algo, file.name, digest(file, algo)))
elif opts.op == 'enc':
	from Crypto import Random
	algo, mode, pad, doiv = crypto(opts)
	key, iv, salt = kis(opts.password.encode('UTF-8'), rand=Random.new(),
						keylen=algo.key_size[0],
						ivlen=algo.block_size if doiv else 0)
	if len(salt) > 0:
		opts.outfile.write(salt)
	if len(iv) > 0:
		opts.outfile.write(iv)
	enc(opts.infile, opts.outfile, algo, mode, key, iv, pad, hash(opts.hash))
elif opts.op == 'dec':
	salt = opts.infile.read(8)
	algo, mode, pad, doiv = crypto(opts)
	iv = opts.infile.read(algo.block_size) if doiv else None
	key = kis(opts.password.encode('UTF8'), iv=iv, salt=salt,
			  keylen=algo.key_size[0],
			  ivlen=algo.block_size if doiv else 0)
	dec(opts.infile, opts.outfile, algo, mode, key, iv, pad, hash(opts.hash))
else:
	print("unexpected command: %s" % opts.op)
