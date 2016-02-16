
# FC: ne pas recréer un Random à chaque fois ? padding ?
#     version dans hash maintenant inutile ?
#     tests : éviter les chemins en durs ?!

from Crypto.Cipher import AES,ARC4
from Crypto.Hash import MD5,SHA256,SHA512
from os import urandom
import sys
from Crypto import Random
import unicodedata

class SIDCrypto:
    def __init__(self, password, algo_cipher=AES, cipher_mode=AES.MODE_CBC, algo_hash = "SHA256", keylen=16, ivlen=16, saltlen=8):
        self.algo_cipher = algo_cipher
        self.cipher_mode = cipher_mode
        
        b = bytearray()
        b.extend(map(ord, password))
        self.password = b

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
            #c=c.decode('utf-8')
            #unicodedata.normalize('NFKD',c).encode('ascii','ignore')
            return b'encrypt: ' + c #the output is the clear message

        else:
            (key,iv,salt) = self.key_iv_salt_generator(password)
            
            cipher = AES.new(key, self.cipher_mode, iv) #a cipher is generated
            
            #print(AES.block_size)
            
            o = open(path, 'rb')
            c = cipher.encrypt(o.read()) #the file is ciphered
            o.close()
            
            c += iv #the iv is appended to the ciphered message
            c += salt #the salt is appended to the ciphered message after the iv
            
            #print(c)
            #print(iv)
            #print(salt)
            #c=c.decode('utf-8')
            #unicodedata.normalize('NFKD',c).encode('ascii','ignore')
            return c #the output is a string containing the ciphered message + the encrypted iv


###DECRYPTION FUNCTION
    def decrypt(self,path,password):
        
        o = open(path, 'rb')
        c = o.read()

        m = self.decryptString(c,password)

        return m #the output is a string containing the message.

    def decryptString(self,s,password):
        
        if self.algo_cipher is None:
            assert s[:9] == b'encrypt: '
            return s[9:]           #it is possible not to encrypt anything by assigning "None" to "algo_cipher". Useful for debugging.

        else:
            c , iv, salt = s[:len(s)-(self.saltlen + self.ivlen)] , s[len(s)-(self.ivlen+self.saltlen):len(s)-self.saltlen] , s[len(s)-self.saltlen:] #the string is splitted into the actual ciphered message, the iv, and the salt
            password_bytes = password.encode('utf-8')
            key = self.hash(password_bytes+salt , converting_bytes = True) #the key is the hash of the password+the salt

            cipher = AES.new(key, self.cipher_mode, iv)
            m = cipher.decrypt(c)

           # m=m.decode('utf-8')
           # unicodedata.normalize('NFKD',m).encode('ascii','ignore')

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

rand=Random.new()
keylen = 16

password = "msi2014"
sid = SIDCrypto(password, algo_cipher=None)
                
message_clair =b"abcdefghijklmnopqrstuvwxyzabcdef\n"
clear = open("/home/baptiste/msi-p14/clear.txt", 'bw')
clear.write(message_clair)
clear.close()

message_chiffre = sid.encrypt("/home/baptiste/msi-p14/clear.txt")

encrypted = open("/home/baptiste/msi-p14/encrypted.txt", 'bw')
encrypted.write(message_chiffre)
encrypted.close()
#encrypted = open("/home/baptiste/msi-p14/encrypted.txt", 'br')

decrypted = open("/home/baptiste/msi-p14/decrypted.txt", 'bw')
decrypted.write(sid.decrypt("/home/baptiste/msi-p14/encrypted.txt", 'msi2014'))
decrypted.close()
