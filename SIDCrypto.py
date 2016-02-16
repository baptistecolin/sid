from Crypto.Cipher import AES,ARC4
from Crypto.Hash import MD5, SHA256, SHA512
from os import urandom
import sys

class SIDCrypto:
    def __init__(self, key, algo_cipher="AES", cipher_mode="AES.MODE_CBC", algo_hash = "SHA256"):
        self.algo_cipher = algo_cipher
        self.cipher_mode = cipher_mode
        self.key = key
        self.algo_hash = algo_hash


###ENCRYPTION FUNCTION
    def encrypt(self, path): #the path is the one of the file that will be ciphered

        iv = urandom(16) #randomly generated iv
        ivCipher = ARC4.new(str(self.key))
        iv = ivCipher.encrypt(iv) #the iv is encrypted using RC4 - whic doesnt require an IV - using the usual key
        iv = int.from_bytes(iv,byteorder = "big")

        cipher = AES.new(self.key, self.cipher_mode, iv) #a cipher is generated

        o = open(path, 'rb')
        c = cipher.encrypt(o.read()) #the file is ciphered
        o.close()
        
        c += iv #the encrypted iv is appended to the ciphered message

        return c #the output is a string containing the ciphered message + the encrypted iv


###DECRYPTION FUNCTION
    def decrypt(self,path):
        
        o = open(path, 'rb')
        c = o.read()

        m = self.decryptString(c)

        return m #the output is a string containing the message.

    def decryptString(self,s):

        c , iv = s[:len(s)-16] , s[len(s)-16:len(s)] #the string is splitted into the actual ciphered message and the crypted iv

        ivCipher = ARC4.new(self.key)
        iv = ivCipher.decrypt(iv) #the crypted iv is decrypted using the key

        cipher = (self.algo_cipher).new(self.key, self.cipher_mode, iv)
        m = cipher.decrypt(c)

        return m #the output is a string containing the message.

###HASH FUNCTION

    def hash(self, name, version = -1):
        if version == -1:
            s = name
        else:
            s = name + str(version)
        s = s.encode("utf-8")
        
        if self.algo_hash == "MD5":
            h = MD5.new()
        
        elif self.algo_hash == "SHA256":
            h = SHA256.new()
        
        elif self.algo_hash == "SHA512":
            h = SHA512.new()

        h.update(s)
        return h.digest()

k = (12345689).to_bytes(9,byteorder =  "big")
sid = SIDCrypto(k, "AES","AES.MODE_CBC","SHA256")

message_chiffre = sid.encrypt("/home/baptiste/msi-p14/clear.txt")
clear.close()

encrypted = open("/home/baptiste/msi-p14/encrypted.txt", 'w')
encrypted.write(message_chiffre)
encrypted.close()
encrypted = open("/home/baptiste/msi-p14/encrypted.txt", 'r')

decrypted = open("/home/baptiste/msi-p14/decrypted.txt", 'w')
decrypted.write(encrypted.read())
