import telepot
import sys
import time
import face_recognition
from telepot.loop import MessageLoop
from collections import defaultdict
import os
import ssl
import urllib.request
import cv2

image_folder = "/Users/Merey/Documents/ai_folder/unknown/"
people_folder = "/Users/Merey/Documents/ai_folder/known/"
query_file = "http://api.telegram.org/file/bot634063576:AAGMuj9nC9Z7e_UJO44bac5elLpeVs9h-cc/"

REGISTERED = 1
NOT_REGISTERED = 0

bot = telepot.Bot('634063576:AAGMuj9nC9Z7e_UJO44bac5elLpeVs9h-cc')

dict_users = {}
dict_usernames  = {}
dict_photos = defaultdict(list)
encodings_faces = {}

def register(chat_id):
	if chat_id not in dict_users :
		hello_message = "Hey, this is the AITagger Bot \n Please, send us your selfie!"
		bot.sendMessage(chat_id, hello_message)
		return NOT_REGISTERED
	return REGISTERED

def sendToEveryone(chat_id, file_id, username):
	bot.download_file(file_id, "./2.jpg")
	new_image = face_recognition.load_image_file("./2.jpg")
	rgb_frame = cv2.cvtColor(new_image, cv2.COLOR_BGR2RGB)
	face_loc = face_recognition.face_locations(rgb_frame, number_of_times_to_upsample = 2)
	new_faces = face_recognition.face_encodings(rgb_frame, num_jitters=100, known_face_locations = face_loc)
	sendTo = "Send to "
	foundFaces = False;
	if len(new_faces) > 0:
		for new_face in new_faces:
			for (key, val) in encodings_faces.items():
				matches =  face_recognition.compare_faces([val], new_face)
				if True in matches and key != chat_id:
					foundFaces = True
					bot.sendPhoto(key, file_id)
					bot.sendMessage(key, "Shared by @" + username)
					sendTo = sendTo +" @"+  dict_usernames[key]

		if foundFaces : 
			bot.sendMessage(chat_id, sendTo)
		else:
			bot.sendMessage(chat_id, "Sorry, there is no people to send")

	else:
		bot.sendMessage(chat_id, "Sorry, I could not recognize any face:( \n Please, send and another photo!")
	


def on_chat_message(msg):
	content_type, chat_type, chat_id = telepot.glance(msg)
	print(msg)
	
	if content_type == 'text':
		register(chat_id)
		if msg['text'] == 'give':	
			print(dict)		



	if content_type =='document':
		bot.sendMessage(chat_id, "Please, send me your photo as a photo attachment")

	if content_type =='photo':
		if chat_id not in dict_users:
			# file_id = msg['document']['file_id']
			file_id = msg['photo'][1]['file_id']
			
			print(file_id)
			file_path = bot.getFile(file_id)['file_path']
			# bot.download_file(file_id, "./1.jpg")
			gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)

			
			f = open('1.jpg','wb')
			f.write(urllib.request.urlopen(query_file + file_path, context = gcontext ).read())
			f.close()

			face_image = face_recognition.load_image_file("./1.jpg")
			rgb_frame = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
			face_loc = face_recognition.face_locations(rgb_frame, number_of_times_to_upsample = 2)
			enc = face_recognition.face_encodings(rgb_frame, known_face_locations = face_loc,  num_jitters=100)


			if len(enc) == 1:
				encodings_faces[chat_id] = enc[0]
				bot.sendMessage(chat_id, "Thank you for registration! Now you can start sending and receiving photos!!!")
				dict_users[chat_id] = file_id
				if msg['from']['username'] is None:
					dict_usernames[chat_id] = msg['from']['first_name']
				else:
					dict_usernames[chat_id] = msg['from']['username']
			elif len(enc) > 1:
				bot.sendMessage(chat_id, "Sorry, I see many faces here:( Can you send me a selfie of yourself, please?")


			else:
				bot.sendMessage(chat_id, "Sorry, I could not recognize any face:( \n Please, send an another photo!")
			

		else:
			username = msg['from']['username']
			file_id = msg['photo'][1]['file_id']
			print(file_id)
			dict_photos[chat_id].append(file_id)
			sendToEveryone(chat_id, file_id, username)

		

def on_callback_query(msg):
	query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
	print('Callback Query:', query_id, from_id, query_data)
	bot.answerCallbackQuery(query_id, text='Got it')

MessageLoop(bot, {'chat': on_chat_message,'callback_query': on_callback_query}).run_as_thread()

print('Listening ...')



while 1:
	time.sleep(10)

