#coding=utf-8

from server_connection import server_connection
import imaplib
import email 
import time 
import base64
import getpass

class Imaps(server_connection):
	
	def __init__(self, login, password, server='imap.gmail.com', name=b'?'):
		self.name = name
		self.mail = imaplib.IMAP4_SSL(server)
		self.mail.login(login, password) #('myusername@gmail.com', 'mypassword')
		
	def affichage(self):
		for list in (self.mail.list()[1]):
			print(bytes.decode(list))
					
	# k est le hash du nom et v est le content qui a été encodé 
	def put(self, k, v, box='OTHERS', flag = '\Flagged'):
		# MessageId: k k est bytes
		# ...
		message = b'Message-Id: ' + k + b'\n'
		message += b'Subject: sid-' + self.name + b'-' + k + b'\n'
		message += b'From: x\n'
		message += b'To: y\n'
		message += b'\n'
		message += base64.b64encode(v)	#'base64' imported, v est bytes
		self.mail.append(box, flag, time.time(), message)
			# ajouter un mail contenu dans box 'OTHERS'
			# flags peut être FLAGS (NonJunk \Draft \Answered \Flagged \Deleted \Seen \Recent)
    		#créer sur le serveur le fichier envoyé, ou le modifier s'il existe déjà
	    
	# donner la clé k, récupérer le fichier 
	def get(self,k, box='OTHERS') :
		self.mail.select(box)
		# 1 UID SEARCH HEADER Message-ID "k..."
		#t, l = self.mail.search(None, '(HEADER Message-ID "<>")', k)
		subject = bytes.decode(b'sid-' + self.name + b'-' + k)
		result, data = self.mail.uid('search', None, 'Header Subject' + ' ' + subject)
		if len(data[0]) > 0: latest_email_uid = data[0].split()[-1]		
		else:	
			print('no result from key -- ' , k)
			return None 
				# , form de bytes, Le plus récent email dans un mail list
		result, data = self.mail.uid('fetch', latest_email_uid, 'BODY[TEXT]')
		raw_email = data[0][1]
				# raw_email is the body text of the email
				# result, data = self.mail.uid('fetch', latest_email_uid, '(RFC822)')
				# data[0][1] bytes 

		if len(raw_email)%4:
			raw_email += b' '*(4 - len(raw_email)%4)	 # length has to be multiple of 4 to be decoded
		raw_decode = base64.b64decode(raw_email)	
		print("the decoded context is \n", bytes.decode(raw_decode))	# GB2312, base64
		w = open("mail_body.txt", 'w')
		w.write(bytes.decode(raw_decode))	
		w.close()
		
		print('\n')
		print('raw email: ')
		result1, data1 = self.mail.uid('fetch', latest_email_uid, '(RFC822)')
		raw_ = data1[0][1]
		print(raw_)
		r = open("mail_raw.txt", 'w')
		r.write(bytes.decode(raw_))
		r.close() 
		
		print('\n')
		email_message = email.message_from_bytes(raw_)  
		print(email_message)
					#for i in email_message.items(): print(i[0], i[1])
					#print('from: ', email.utils.parseaddr(email_message['From']))
    				#récupérer le fichier à partir de sa clé (hash du nom)
    				
	def delete(self, k) :
		self.mail.select('[Gmail]/&YkBnCZCuTvY-')   #mail box ALL
		subject = bytes.decode(b'sid-' + self.name + b'-' + k)
		result, data = self.mail.uid('search', None, 'Header Subject' + ' ' + subject)
		if len(data[0]) > 0: latest_email_uid = data[0].split()	
		else:	
			print('no result from key -- ' , k)
			return None 
		print("find the key", k, 'in', data[0], 'mails')
		for uid in latest_email_uid:
			result1, data1 = self.mail.uid('STORE', uid, '+X-GM-LABELS', '\\Trash')	
			if result1 == 'OK': 
				print("the email with key ", k, "UID = ", uid, "has been marked deleted. ")
			else:	
				print("the latest email with key ", k, "UID = ", uid, "hasn't been found or failed to delete. ")
		self.mail.select('[Gmail]/&XfJSIJZkkK5O9g-')	#mail box Trash
		self.mail.store("1:*", '+FLAGS', '\\Deleted')
		self.mail.expunge()
			# delete the kth email received and from the 'inbox', in gmail the deleted
			# mail can still be found in the "ALL Mail"
			# 删除第k封收到的邮件，
    		#supprimer le fichier à partir de sa clé
'''
	def  __contains__(self, key) :
		print("this is contains")
    		#histoire qu'on puisse utiliser "if key in list"
	
	def __delitem__(self, key) :
		pass
    		#pour que delete self[key] ait un sens
	
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
	IM = Imaps('xiangnan.chat@gmail.com', password, name=b'test')
	IM.affichage()
	for i in range(5):
		IM.put(b'ok', b'blablablablablabla', 'INBOX')
	IM.get(b'okthenk')
	#IM.get(b'hello2')
	IM.delete(b'ok')
	
	#MP = Imaps('xiangnan.yue@mines-paristech.fr','','imapel.ensmp.fr')
	#MP.affichage()