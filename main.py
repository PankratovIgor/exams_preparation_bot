import telebot
import sqlite3
from functools import partial
from secrets import tg_token

bot = telebot.TeleBot(tg_token)
db = sqlite3.connect('test.db', isolation_level=None, check_same_thread=False)
cur = db.cursor()

@bot.message_handler (commands=['start'])
def start(message):
  chat_id = message.chat.id
  exists = cur.execute("SELECT * FROM users WHERE id = ?", [chat_id]).fetchone()
  print(exists)
  if exists:
    bot.send_message(chat_id, 'Вы уже пользуетесь ботом, добро пожаловать!')
  else:
    msg = bot.reply_to(message, 'Здравствуйте! Я телеграм бот для подготовки к экзаменам. Напишите, пожалуйста как к Вам можно обращаться.')
    bot.register_next_step_handler(msg, process_name_user_step)

def process_name_user_step(message):
  name = message.text
  user_id = message.chat.id
  bot.send_message(user_id, 'Отлично! Я запомнил Вас.')
  cur.execute('INSERT INTO users (id, name) VALUES (?, ?)', (user_id, name))

@bot.message_handler (commands=['add_exam'])
def add_exam(message):
  msg = bot.reply_to(message, 'Укажите, пожалуйста, название экзамена.')
  bot.register_next_step_handler(msg, process_name_step)

def process_name_step(message):
  try:
    name = message.text
    msg = bot.reply_to(message, 'Укажите дату экзамена.')
    bot.register_next_step_handler(msg, partial(process_date_step, name))
  except Exception as e:
    bot.reply_to(message, 'oooops')

def process_date_step(name, message):
  try:
    date = message.text
    msg = bot.reply_to(message, 'Укажите место проведения экзамена.')
    bot.register_next_step_handler(msg, partial(process_place_step, name, date))
  except Exception as e:
    bot.reply_to(message, 'oooops')

def process_place_step(name, date, message):
  chat_id = message.chat.id
  place = message.text
  cur.execute('SELECT COUNT(*) from exams')
  exam_id = cur.fetchone()[0]
  user_id = message.chat.id
  bot.reply_to(message, 'Отлично! Экзамен записан.')
  cur.execute('INSERT INTO exams (id, owner_id, name, date, place) VALUES (?, ?, ?, ?, ?)', (exam_id, user_id, name, date, place))
  cur.execute('INSERT INTO has_access (user_id, exam_id) VALUES (?, ?)', (chat_id, exam_id))
  

bot.polling(none_stop = True)