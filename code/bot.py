import telebot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import TOKEN, ADMINS_ID

bot = telebot.TeleBot(token=TOKEN)


# todo: сделать requeriments
# todo: доработать структуру бд
# todo: оформить получение ответа от нейронки
# todo: добавить проверку токенов
# todo: написать логику диалога


@bot.message_handler(commands=['debug'])
def send_debug_file(message):
    user_id = message.chat.id
    if user_id in ADMINS_ID:
        with open('other/logConfig.log', 'rb') as file:
            f = file.read()
        bot.send_document(message.chat.id, f, visible_file_name='other/logConfig.log')
    else:
        bot.send_message(user_id, 'у вас нет прав')


@bot.message_handler(commands=['help'])
def help(message: Message):
    bot.send_message(message.chat.id, """
/start - команда для запуска бота
/help - список команд
/stop - остановка диалога
/continue - продолжение диалога
    """)


@bot.message_handler(commands=['start'])
def start(message: Message):
    pass

