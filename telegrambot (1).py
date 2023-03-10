# -*- coding: utf-8 -*-
"""Telegrambot.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/171fpOoB1HHr_6b0iOC3Kc88n9BADefVM
"""

pip install Wikipedia

pip install pyTelegramBotAPI

pip install scikit-learn

pip install SpeechRecognition

import os
import requests
import speech_recognition as sr
import subprocess
import datetime
import telebot, wikipedia, re
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression

bot = telebot.TeleBot('5896628221:AAHBP4-TBFwM6U9KACCjUW9tUARSj9Q6Hzs')
wikipedia.set_lang("ru")

def clean_str(r):
	r = r.lower()
	r = [c for c in r if c in alphabet]
	return ''.join(r)

alphabet = ' 1234567890-йцукенгшщзхъфывапролджэячсмитьбюёqwertyuiopasdfghjklzxcvbnm?%.,()!:;'

def update():
	with open('/content/drive/MyDrive/Colab Notebooks/dialogues.txt', encoding='utf-8') as f:
		content = f.read()
	
	blocks = content.split('\n')
	dataset = []
	
	for block in blocks:
		replicas = block.split('\\')[:2]
		if len(replicas) == 2:
			pair = [clean_str(replicas[0]), clean_str(replicas[1])]
			if pair[0] and pair[1]:
				dataset.append(pair)
	
	X_text = []
	y = []
	
	for question, answer in dataset[:10000]:
		X_text.append(question)
		y += [answer]
	
	global vectorizer
	vectorizer = CountVectorizer()
	X = vectorizer.fit_transform(X_text)
	
	global clf
	clf = LogisticRegression()
	clf.fit(X, y)

update()

def get_generative_replica(text):
	text_vector = vectorizer.transform([text]).toarray()[0]
	question = clf.predict([text_vector])[0]
	return question

def getwiki(s):
    try:
        ny = wikipedia.page(s)
        wikitext=ny.content[:1000]
        wikimas=wikitext.split('.')
        wikimas = wikimas[:-1]
        wikitext2 = ''
        for x in wikimas:
            if not('==' in x):
                if(len((x.strip()))>3):
                   wikitext2=wikitext2+x+'.'
            else:
                break
        wikitext2=re.sub('\([^()]*\)', '', wikitext2)
        wikitext2=re.sub('\([^()]*\)', '', wikitext2)
        wikitext2=re.sub('\{[^\{\}]*\}', '', wikitext2)
        return wikitext2
    except Exception as e:
        return 'В Википедии нет информации об этом'

@bot.message_handler(commands=['start'])
def start_message(message):
	bot.send_message(message.chat.id,"Здравствуйте, Сэр.")

question = ""

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
	command = message.text.lower()
	if command =="не так":
		bot.send_message(message.from_user.id, "а как?")
		bot.register_next_step_handler(message, wrong)
	else:
		global question
		question = command
		reply = get_generative_replica(command)
		if reply=="вики ":
			bot.send_message(message.from_user.id, getwiki(command))
		else:
			bot.send_message(message.from_user.id, reply)

def wrong(message):
	a = f"{question}\{message.text.lower()} \n"
	with open('dialogues.txt', "a", encoding='utf-8') as f:
		f.write(a)
	bot.send_message(message.from_user.id, "Готово")
	update()

@bot.message_handler(content_types=['voice'])
def get_audio_messages(message):

    try:
        print("Started recognition...")

        file_info = bot.get_file(message.voice.file_id)
        path = os.path.splitext(file_info.file_path)[0]
        fname = os.path.basename(path) 
        doc = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format('5896628221:AAHBP4-TBFwM6U9KACCjUW9tUARSj9Q6Hzs', file_info.file_path))
        with open(fname+'.oga', 'wb') as f:
            f.write(doc.content)
        process = subprocess.run(['ffmpeg', '-i', fname+'.oga', fname+'.wav'])
        result = audio_to_text(fname+'.wav') 
        question = get_generative_replica(format(result))
        bot.reply_to(message, question)
    except sr.UnknownValueError as e:
        bot.send_message(message.from_user.id,  "Прошу прощения, но я не разобрал сообщение...")
        with open(logfile, 'a', encoding='utf-8') as f:
            f.write(str(datetime.datetime.today().strftime("%H:%M:%S")) + ':' + str(message.from_user.id) + ':' + str(message.from_user.first_name) + '_' + str(message.from_user.last_name) + ':' + str(message.from_user.username) +':'+ str(message.from_user.language_code) + ':Message is empty.\n')
    except Exception as e:
        bot.send_message(message.from_user.id,  "Что-то пошло не так...")
        
        with open(logfile, 'a', encoding='utf-8') as f:
            f.write(str(datetime.datetime.today().strftime("%H:%M:%S")) + ':' + str(message.from_user.id) + ':' + str(message.from_user.first_name) + '_' + str(message.from_user.last_name) + ':' + str(message.from_user.username) +':'+ str(message.from_user.language_code) +':' + str(e) + '\n')
    finally:
        os.remove(fname+'.wav')
        os.remove(fname+'.oga')

def audio_to_text(dest_name: str):
    r = sr.Recognizer()
    message = sr.AudioFile(dest_name)
    with message as source:
        audio = r.record(source)
    result = r.recognize_google(audio, language="ru_RU")
    return result

bot.polling(none_stop=True)