import telebot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from data import get_table_data, is_user_in_table, add_new_user, update_row, settings_dict
from config import TOKEN, ADMINS_ID, MAX_USERS
from gpt import ask_gpt_helper

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


def gen_settings_markup(params_list_name: str, set: str):
    markup = InlineKeyboardMarkup()
    for name in settings_dict[params_list_name]:
        markup.add(InlineKeyboardButton(name, callback_data=name + '_' + set + '_choice'))
    return markup


def settings_choice_1(user_id):
    bot.send_message(user_id, 'выбери персонажа:', reply_markup=gen_settings_markup('characters_list', 'character'))
    settings_choice_2(user_id)


def settings_choice_2(user_id):
    bot.send_message(user_id, 'выбери жанр:', reply_markup=gen_settings_markup('genres_list', 'genre'))
    settings_choice_3(user_id)


def additions_1(user_id):
    msg = bot.send_message(user_id, 'какие-то дополнения? (напиши "-" если их нет)')
    bot.register_next_step_handler(msg, additions_2)


def settings_choice_3(user_id):
    bot.send_message(user_id, 'выбери локацию:', reply_markup=gen_settings_markup('locations_list', 'location'))
    additions_1(user_id)


def additions_2(message: Message):
    user_id = message.chat.id
    if message.text == '-':
        dialogue_start(user_id)
    else:
        add_promt = message.text
        update_row(user_id, 'addition', add_promt)





@bot.callback_query_handler(func=lambda call: call.data.endswith('choice'))
def set_change(call):
    user_id = call.message.chat.id
    param = call.data.split('_')[0]
    set = call.data.split('_')[1]
    bot.delete_message(user_id, call.chat.message_id)
    update_row(user_id, set, param)
    bot.send_message(user_id, 'настройки выбраны!')


def user_request(user_id):
    msg = bot.send_message(user_id, 'как повернет сюжет дальше?')
    bot.register_next_step_handler(msg, dialogue)


def dialogue_start(user_id):
    ask_gpt_helper()


@bot.message_handler(content_types=['text'])
def dialogue(message):
    ask_gpt_helper()





bot.infinity_polling()
