from Crypto.Cipher import AES,ARC4,ARC2,Blowfish,CAST,DES,DES3
from Crypto.Hash import MD5,SHA256,SHA512
from Crypto import Random
from SIDStructure import *

class Null:
    def new(key, mode, iv):
        res = NullCipher(key, mode, iv)
        return res

    MODE_CBC = True
    key_size = [8]
    block_size = 8

class NullCipher:
    def __init__(self, key, mode, iv):
        self.key = key
        self.mode = mode
        self.iv = iv
        self.block_size = 8

    def encrypt(self, s):
        assert len(s)%self.block_size == 0
        return s

    def decrypt(self, s):
        return s

algos = {"AES":AES, "ARC2":ARC2, "ARC4":ARC4, "Blowfish":Blowfish, "DES":DES, "CAST":CAST, "DES3":DES3, "SHA256":SHA256, "SHA512":SHA512, \
         "MD5":MD5, "None":Null}

class SIDCrypto:
    def __init__(self, password, algo_cipher="AES", algo_hash = "SHA256", saltlen = 8, globalkeylen = 32):
        self.password = password
        self.algo_hash = algos[algo_hash]
        self.saltlen = saltlen
        self.globalkeylen = globalkeylen

        self.algo_cipher = algos[algo_cipher]

        if self.algo_cipher == DES: #DES implementation is different...
            self.keylen, self.ivlen = DES.key_size, DES.block_size
        else:
            self.keylen, self.ivlen = self.algo_cipher.key_size[-1], self.algo_cipher.block_size

        self.rand = Random.new()
        self.globalKey = None

    def globalKeyGenerator():
        return self.rand(self.globalkeylen)


    def key_iv_salt_generator(self,globalKey):
        iv = (self.rand).read(self.ivlen) #random generation of the iv
        salt = (self.rand).read(self.saltlen) #random generation of the salt
        
        assert self.globalKey != None #error thrown if globalKey has not been defined

        key = self.hash(globalKey + salt , converting_bytes = True) #the key is the hash of the global key +the salt
        key = key[:self.keylen]
        
        return (key,iv,salt)        


###ENCRYPTION FUNCTION
    def encrypt(self, path, usePassword = False):
        #the path is the one of the file that will be ciphered

        o = open(path, 'rb')
        clear = o.read() #message contained in the file
        o.close()

        m = self.encryptBytes(clear, usePassword)
        
        return m

    def encryptBytes(self, clear, usePassword = False):
        if not usePassword :
            (key,iv,salt) = self.key_iv_salt_generator(self.globalKey)
        else:
            password_bytes = self.password.encode('utf-8')
            (key,iv,salt) = self.key_iv_salt_generator(password_bytes)
    
        #generating a cipher
        if self.algo_cipher == ARC2:
            cipher = ARC2.new(key)
        else:
            cipher = self.algo_cipher.new(key, self.algo_cipher.MODE_CBC, iv)

        clear += self.hash(clear)
        
        #begin padding
        padlen = cipher.block_size
        if padlen != len(clear)%padlen:
            padlen = padlen - (len(clear)%padlen)
        clear += bytearray((chr(padlen)*padlen).encode("utf-8"))
           
        c = cipher.encrypt(clear) #the message is ciphered           
            
        c += iv #the iv is appended to the ciphered message
        c += salt #the salt is appended to the ciphered message after the iv
        
        return c #the output is a bytes array containing the ciphered message + the encrypted iv




###DECRYPTION FUNCTION
    def decrypt(self,path, usePassword = False):
        
        o = open(path, 'rb')
        c = o.read()

        m = self.decryptBytes(c, usePassword)

        return m #the output is a byte array containing the message.

    def decryptBytes(self,s, usePassword = False):
        #the string is splitted into the actual ciphered message, the hash, the iv, and the salt
        c = s[:len(s)-(self.saltlen + self.ivlen)]
        iv = s[len(s)-(self.ivlen+self.saltlen):len(s)-self.saltlen]
        salt = s[len(s)-self.saltlen:]

        assert self.globalKey != None #an error is thrown if globalKey has not been defined

        #the key is the hash of the password+the salt
        if not usePassword :
            key = self.hash(self.globalKey + salt , converting_bytes = True)
        else :
            password_bytes = self.password.encode('utf-8')
            key = self.hash(password_bytes + salt , converting_bytes = True)


        if self.algo_cipher == ARC2:
            cipher = ARC2.new(key)
        else:
            cipher = self.algo_cipher.new(key, self.algo_cipher.MODE_CBC, iv)
            
        m = cipher.decrypt(c)
            
        assert len(m)%(cipher.block_size) == 0 #makes sure m is conveniently padded. Else, throws an error.

        #begin unpadding
        padlen = m[-1]
        m = m[:-padlen]

        #integrity control
        assert self.hash(m[:-self.algo_hash.digest_size], converting_bytes = True) == m[-self.algo_hash.digest_size:]
        
        return m[:-self.algo_hash.digest_size] #the output is a byte array containing the message.

###HASH FUNCTION
    def hash(self, name, version = -1, converting_bytes = False, hash_file = False):
        
        if (not converting_bytes):
            if hash_file:
                f = open(name,'br')
                s = f.read()
            else:
                if version == -1:
                    s = name
                else:
                    s = name + str(version)
                    s = s.encode("utf-8")
        else:
            s = name

        h = self.algo_hash.new()  
        h.update(s)
        return h.digest()

if __name__ == "__main__":
    import getpass
    password = getpass.getpass('password: ')
    algo = input("algorithme a utiliser : ")
    sid = SIDCrypto(password, algo_cipher=algo)
    sid.globalKey = sid.rand.read(sid.globalkeylen)
                
    message_clair = input("message a chiffrer : ").encode('utf-8')
    clear = open("clear.txt", 'bw')
    clear.write(message_clair)
    clear.close()

    message_chiffre = sid.encrypt("clear.txt")

    encrypted = open("encrypted.txt", 'bw')
    encrypted.write(message_chiffre)
    encrypted.close()

    decrypted = open("decrypted.txt", 'bw')
    decrypted.write(sid.decrypt("encrypted.txt"))
    decrypted.close()
