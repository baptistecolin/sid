# -*- coding:utf-8 -*-

from server_connection import server_connection
import imaplib
import email 
import time 
import base64
import getpass

class Imaps(server_connection):
	
	def __init__(self, login, password, server='imap.gmail.com',
				 name='?', box='OTHERS', flag='\Flagged'):
		self.name = name
		self.box = box
		self.flag = flag
		self.mail = imaplib.IMAP4_SSL(server)
		self.mail.login(login, password) #('myusername@gmail.com', 'mypassword')
<<<<<<< HEAD
		self.mail.create(box)
		
=======
		self.mail.create('OTHERS')
>>>>>>> 3228b1882ddecb1cd96606d206c239bd2e026a4e
	def affichage(self):
		for list in (self.mail.list()[1]):
			print(bytes.decode(list))
	
<<<<<<< HEAD
	def create_box(self, box = 'OTHERS'):
		self.mail.create(box)
	
=======
	# k : string
	# keyId : bytes
>>>>>>> 3228b1882ddecb1cd96606d206c239bd2e026a4e
	def keyId(self, k):
		return b'sid-' + bytes(self.name, 'utf-8') + b'-' + bytes(k, 'utf-8')
					
	# k est le hash du nom et v est le content qui a été encodé 
	def put(self, k, v):
		# MessageId: k k est bytes
		# ...
		message = b'Message-Id: ' + bytes(k, 'utf-8') + b'\n'
		message += b'Subject: ' + self.keyId(k) + b'\n'
		message += b'From: x\n'
		message += b'To: y\n'
		message += b'\n'
		message += base64.b64encode(v)	#'base64' imported, v est bytes
		self.mail.append(self.box, self.flag, time.time(), message)
			# ajouter un mail contenu dans box 'OTHERS'
			# flags peut être FLAGS (NonJunk \Draft \Answered \Flagged \Deleted \Seen \Recent)
    		#créer sur le serveur le fichier envoyé, ou le modifier s'il existe déjà
	    
	# donner la clé k, récupérer le fichier 
	def get(self, k) :
		self.mail.select(self.box)
		# 1 UID SEARCH HEADER Message-ID "k..."
		#t, l = self.mail.search(None, '(HEADER Message-ID "<>")', k)
		subject = bytes.decode(self.keyId(k))
		result, data = self.mail.uid('search', None, 'Header Subject ' + subject)
		if len(data[0]) > 0:
			latest_email_uid = data[0].split()[-1]		
			
		else:	
			print('no result from key -- ' , k)
			return False 
				# , form de bytes, Le plus récent email dans un mail list
		result, data = self.mail.uid('fetch', latest_email_uid, 'BODY[TEXT]')
		#raw_email = 
				# raw_email is the body text of the email
				# result, data = self.mail.uid('fetch', latest_email_uid, '(RFC822)')
				# data[0][1] bytes 

		#if len(raw_email)%4:
		#	raw_email += b' '*(4 - len(raw_email)%4)	 # length has to be multiple of 4 to be decoded
		raw_decode = base64.b64decode(data[0][1])	
		#print("the decoded context is \n", bytes.decode(raw_decode))	# GB2312, base64
		return raw_decode
		#w = open("mail_body.txt", 'w')
		#w.write(bytes.decode(raw_decode))	
		#w.close()
		
		#print('\n')
		#print('raw email: ')
		#result1, data1 = self.mail.uid('fetch', latest_email_uid, '(RFC822)')
		#raw_ = data1[0][1]
		#print(raw_)
		#r = open("mail_raw.txt", 'w')
		#r.write(bytes.decode(raw_))
		#r.close() 
		
		#print('\n')
		#email_message = email.message_from_bytes(raw_)  
		#print(email_message)
					#for i in email_message.items(): print(i[0], i[1])
					#print('from: ', email.utils.parseaddr(email_message['From']))
    				#récupérer le fichier à partir de sa clé (hash du nom)
    				
	def delete(self, k) :
		self.mail.select(self.box)   #mail box ALL
		subject = bytes.decode(self.keyId(k))
		result, data = self.mail.uid('search', None, 'Header Subject' + ' ' + subject)
		if len(data[0]) > 0: 
			latest_email_uid = data[0].split()	
		else:	
			print('no result from key -- ' , k)
			return None 
		print("find the key", k, 'in', data[0], 'mails')
		for uid in latest_email_uid:
			result1, data1 = self.mail.uid('STORE', uid, '+X-GM-LABELS', '\\Trash')	
			result2, data2 = self.mail.uid('STORE', uid, 'FLAGS', '\\Deleted')
			if result1 == 'OK' and result2 == 'OK': 
				print("the email with key ", k, "UID = ", uid, "has been moved to Trash box and deleted from box " + self.box)
			else:	
				print("the latest email with key ", k, "UID = ", uid, "hasn't been found or failed to delete. ")
		self.mail.expunge()
		#self.mail.select('[Gmail]/&XfJSIJZkkK5O9g-')	#mail box Trash
		#self.mail.store("1:*", '+FLAGS', '\\Deleted')
		#self.mail.expunge()
			# delete the kth email received and from the 'inbox', in gmail the deleted
			# mail can still be found in the "ALL Mail"
			# 删除第k封收到的邮件，
    		#supprimer le fichier à partir de sa clé
	
	def  __contains__(self, k) :
		self.mail.select(self.box)
		subject = bytes.decode(self.keyId(k))
		result, data = self.mail.uid('search', None, 'Header Subject' + ' ' + subject)
		if len(data[0]) > 0: 
			latest_email_uid = data[0].split()
			#print(len(data[0].split()), "mails found, contained in Mail ", data[0] )
			return True	
		else:	
			#print('no result from key -- ' , k)
			return False 
		
		
    		#histoire qu'on puisse utiliser "if key in list"

	def __delitem__(self, key) :
		self.delete(key)
    		#pour que del self[key] ait un sens
    		
'''	
	def __eq__(self, value) :
    	pass
		#afin que self==value marche
	def __getitem__(self,x) :
		pass
    		#x.__getitem__(y)<=>x[y]
	
	def __setitem__(self, key, value) :
		pass
    		#set self[key] to value
'''	


if __name__ == '__main__':
	password = getpass.getpass('password: ')
#	IM = Imaps('xiangnan.chat@gmail.com', password, name=b'test')
	IM = Imaps('ribs.sid@gmail.com', password, name='test')
	IM.affichage()
	#for i in range(5):
	IM.put('toto', b'blablablablablabla')
	print("get: ", IM.get('toto'))
	#IM.get(b'hello2')
	
	#IM.__contains__(b'toto'):
	print('toto' in IM)
	
	#IM.delete(b'toto')
	del IM['toto'] 
	
	#MP = Imaps('xiangnan.yue@mines-paristech.fr','','imapel.ensmp.fr')
	#MP.affichage()
