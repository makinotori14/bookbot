#IMPORTING ALL LIBRARIES

import telebot
import sqlite3 
import time

#CONNECTING ALL LIBRARIES

  #connect bot
bot = telebot.TeleBot('')

  #connect db
db_connect = sqlite3.connect('../db/database', check_same_thread=False)
db_cursor = db_connect.cursor()
t = db_cursor.execute("SELECT * FROM Books")
all_books = t.fetchall()

#OWN FUNCTIONS

def search_by_word(string, base):
  L = []
  for k in base:
    if string in k[2].lower():
      L.append(k)
  return L

def search_by_id(val, base):
  for k in base:
    if k[0] == val:
      return k
  return False


#OWN EXCEPTIONS

class WrongID(Exception):
  pass

#MESSAGE ANSWERS

  #start & help answers

@bot.message_handler(commands=['start', 'help'])
def start_help_message(message):
  bot.send_message(
    message.chat.id,
    """Здравствуйте, я бот электронной библиотеки МАОУ СОШ №103. Напишите команду /find, чтобы найти книгу

Формат fb2 или epub.
    """
  )

  #buying book

    #find book by its' title
@bot.message_handler(commands=['find'])
def find_book(message):
  send = bot.send_message(message.chat.id, "Введите название книги:")
  bot.register_next_step_handler(send, title)

    #print results
def title(message):
  book_title = message.text
  bot.send_message(message.chat.id, f'Поиск книги "{book_title}". Подождите, пожалуйста, это займет какой-то время...')
  book_title = book_title.lower() #Transfer it to lower case
  results = search_by_word(book_title, all_books)
  if results:
    answer = ""
    for book in results:
      t = f'{book[2]} — {book[1]} [{book[0]}]\n'
      answer += t
    send = bot.send_message(message.chat.id, "Вот что я нашел:\n\n" + answer + '\n' + "Если вас что-то заинтересовало, напишите ID книги (цифра в квадратных скобках), если нет - напишите 0.\n")
    bot.register_next_step_handler(send, buy, results)
  else:
    bot.send_message(
      message.chat.id,
      """
      Извините, я ничего не нашел :(
      
Напишите команду /add, чтобы я нашел интересующую вас книгу"""
    )

    #buy selected book
def buy(message, results):
  if message.text == '0':
    bot.send_message(message.chat.id ,'Жалко. Напоминаю, что вы можете написать команду /add, если вы не нашли того, что искали')
    return
  try:
    value = int(message.text)
    book = search_by_id(value, results)
    if book:
      send = bot.send_message(
        message.chat.id,
        f'Ваш выбор — "{book[2]}". В этот чат придет файл через несколько секунд.'
      )
      send_file(message, book)
    else:
      raise WrongID
  except:
    bot.send_message(message.chat.id, 'Вы неправильно ввели ID или же такого ID не существует.')

    #send file
def send_file(message, book):
  filename = '' + book[3]
  f = open(filename, 'rb')
  bot.send_document(message.chat.id, f)

  #add answer

@bot.message_handler(commands=['add'])
def add(message):
  send = bot.send_message(message.chat.id, "Напишите мне, какую книгу вы хотели бы приобрести. Мы добавим ее в базу данных в ближайшее время")
  bot.register_next_step_handler(send, notify)
  #anything else

def notify(message):
  bot.send_message(0, message.text)

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
  bot.send_message(message.chat.id, 'Я вас не понимаю :(\nВведите, пожалуйста, /start или /help, если хотите узнать, что я умею')

#STARTING BOT

while True:
  try:
    bot.polling(none_stop=True)
  except:
    time.sleep(2)