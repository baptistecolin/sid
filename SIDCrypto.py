
# FC: ne pas recréer un Random à chaque fois ? padding ?
#     version dans hash maintenant inutile ?
#     tests : éviter les chemins en durs ?!

from Crypto.Cipher import AES,ARC4,ARC2,Blowfish,CAST,DES,DES3
from Crypto.Hash import MD5,SHA256,SHA512
from os import urandom
import sys
from Crypto import Random
import unicodedata

class SIDCrypto:
    def __init__(self, password, algo_cipher="AES", algo_hash = "SHA256", keylen=16, ivlen=16, saltlen=8):
        self.algo_cipher = algo_cipher
        
        self.password = password # password.encode('UTF-8')

        self.algo_hash = algo_hash
        self.keylen = keylen
        self.ivlen = ivlen
        self.saltlen = saltlen
        self.rand = Random.new()

    def key_iv_salt_generator(self,password):
        iv = (self.rand).read(self.ivlen) #random generation of the iv
        salt = (self.rand).read(self.saltlen) #random generation of the salt
        password_bytes = password.encode('utf-8')

        key = self.hash(password_bytes+salt , converting_bytes = True) #the key is the hash of the password+the salt

        return (key,iv,salt)        



###ENCRYPTION FUNCTION
    def encrypt(self, path, keylen=16, ivlen=16, saltlen=8): #the path is the one of the file that will be ciphered

        if (self.algo_cipher == None):
            o = open(path, 'rb')
            c = o.read() #the file is ciphered
            o.close()

            return b'encrypt: ' + c #the output is the clear message

        else:
            (key,iv,salt) = self.key_iv_salt_generator(password)

            #generating a cipher
            if self.algo_cipher == "AES":
                cipher = AES.new(key, AES.MODE_CBC, iv)
            elif self.algo_cipher == "ARC2":
                cipher = ARC2.new(key)
            elif self.algo_cipher == "ARC4":
                cipher = ARC4.new(key, ARC4.MODE_CBC, iv)
            elif self.algo_cipher == "Blowfish":
                cipher = Blowfish.new(key, Blowfish.MODE_CBC, iv)
            elif self.algo_cipher == "DES":
                cipher = DES3.new(key, DES3.MODE_CBC, iv)
            elif self.algo_cipher == "CAST":
                cipher = CAST.new(key, CAST.MODE_CBC, iv)
            elif self.algo_cipher == "DES3":
                cipher = DES.new(key, DES.MODE_CBC, iv)
            #print(cipher.block_size)

            
            o = open(path, 'rb')
            clear = o.read()

            #begin padding
            padlen = cipher.block_size
            if padlen != len(clear)%padlen:
                padlen = padlen - (len(clear)%padlen)
            clear += bytearray((chr(padlen)*padlen).encode("ASCII"))
            
            c = cipher.encrypt(clear) #the file is ciphered
            o.close()
            
            
            c += iv #the iv is appended to the ciphered message
            c += salt #the salt is appended to the ciphered message after the iv
        
            return c #the output is a string containing the ciphered message + the encrypted iv


###DECRYPTION FUNCTION
    def decrypt(self,path):
        
        o = open(path, 'rb')
        c = o.read()

        m = self.decryptString(c,self.password)

        return m #the output is a string containing the message.

    def decryptString(self,s,password):
        
        if self.algo_cipher is None:
            assert s[:9] == b'encrypt: '
            return s[9:]           #it is possible not to encrypt anything by assigning "None" to "algo_cipher". Useful for debugging.

        else:

            #the string is splitted into the actual ciphered message, the iv, and the salt
            c = s[:len(s)-(self.saltlen + self.ivlen)]
            iv = s[len(s)-(self.ivlen+self.saltlen):len(s)-self.saltlen]
            salt = s[len(s)-self.saltlen:]

            password_bytes = password.encode('utf-8')

            #the key is the hash of the password+the salt
            key = self.hash(password_bytes+salt , converting_bytes = True)

            if self.algo_cipher == "AES":
                cipher = AES.new(key, AES.MODE_CBC, iv)
            elif self.algo_cipher == "ARC2":
                cipher = ARC2.new(key)
            elif self.algo_cipher == "ARC4":
                cipher = ARC4.new(key, ARC4.MODE_CBC, iv)
            elif self.algo_cipher == "Blowfish":
                cipher = Blowfish.new(key, Blowfish.MODE_CBC, iv)
            elif self.algo_cipher == "DES":
                cipher = DES3.new(key, DES3.MODE_CBC, iv)
            elif self.algo_cipher == "CAST":
                cipher = CAST.new(key, CAST.MODE_CBC, iv)
            elif self.algo_cipher == "DES3":
                cipher = DES.new(key, DES.MODE_CBC, iv)

            m = cipher.decrypt(c)

            #begin unpadding
            padlen = m[-1]
            #print(padlen)
            m = m[:-padlen]
            #print(len(m))

            return m #the output is a string containing the message.

###HASH FUNCTION
    def hash(self, name, version = -1, converting_bytes = False):
        
        if (not converting_bytes):
            if version == -1:
                s = name
            else:
                s = name + str(version)
            s = s.encode("utf-8")
        
        else:
            s = name

        if self.algo_hash == "MD5":
            h = MD5.new()
            
        elif self.algo_hash == "SHA256":
            h = SHA256.new()
            
        elif self.algo_hash == "SHA512":
            h = SHA512.new()
                
        h.update(s)
        return h.digest()

if False:
    rand=Random.new()
    keylen = 16

    import getpass
    password = getpass.getpass('password: ')
    sid = SIDCrypto(password)
                
    message_clair = input().encode('utf-8')
    clear = open("clear.txt", 'bw')
    clear.write(message_clair)
    clear.close()

    message_chiffre = sid.encrypt("clear.txt")

    encrypted = open("encrypted.txt", 'bw')
    encrypted.write(message_chiffre)
    encrypted.close()
    #encrypted = open("/home/baptiste/msi-p14/encrypted.txt", 'br')

    decrypted = open("decrypted.txt", 'bw')
    decrypted.write(sid.decrypt("encrypted.txt"))
    decrypted.close()
