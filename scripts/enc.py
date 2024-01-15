import os
import json
import jsonpickle
import datetime
import base64 
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad,unpad
import time

class SecureMessage:
     
	key = "i5focfp8npqazhnecfxq5fyvblbwah2z"
	
	def enc(self, raw):
		raw = pad(raw.encode(),16)
		cipher = AES.new(self.key.encode('utf-8'), AES.MODE_ECB)
		return base64.b64encode(cipher.encrypt(raw))

	def decrypt(self, enc):
		enc = base64.b64decode(enc)
		cipher = AES.new(self.key.encode('utf-8'), AES.MODE_ECB)
		return unpad(cipher.decrypt(enc),16)
