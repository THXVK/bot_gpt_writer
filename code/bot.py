import telebot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from data import get_table_data, is_user_in_table, add_new_user, characters_list
from config import TOKEN, ADMINS_ID, MAX_USERS

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
        bot.send_document(message.chat.id, f, visible_file_name='logConfig.log')
    else:
        bot.send_message(user_id, 'у вас нет прав')


@bot.message_handler(commands=['help'])
def help_message(message: Message):
    bot.send_message(message.chat.id, """
/start - команда для запуска бота
/help - список команд
/stop - остановка диалога
/continue - продолжение диалога
    """)


@bot.message_handler(commands=['start'])
def start(message: Message):
    user_id = message.chat.id
    actual_users_num = len(get_table_data())
    if actual_users_num < MAX_USERS and not is_user_in_table(user_id):
        add_new_user(user_id)
        bot.send_message(user_id, 'вы добавлены')
        settings_choice_1(user_id)

    elif is_user_in_table(user_id):
        bot.send_message(user_id, 'вы уже в базе')

    else:
        bot.send_message(user_id, 'база переполнена')


def gen_markup_1():
    markup = InlineKeyboardMarkup()
    for name in characters_list:
        markup.add(InlineKeyboardButton(name, callback_data=name + 'choice'))
    return markup


def settings_choice_1(user_id):
    bot.send_message(user_id, 'выбери персонажа:', reply_markup=gen_markup_1())
