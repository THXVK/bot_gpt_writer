import telebot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from data import get_table_data, is_user_in_table, add_new_user, update_row, settings_dict, actions, get_user_data, \
    clear_user_story_data
from config import TOKEN, ADMINS_ID, MAX_USERS
from gpt import gpt_ask, count_tokens, gpt_start

bot = telebot.TeleBot(token=TOKEN)


# todo: добавить проверку токенов

# region markups
def gen_actions_markup():
    markup = InlineKeyboardMarkup()
    for action in actions:
        markup.add(InlineKeyboardButton(actions[action], callback_data=action))
    return markup


def gen_settings_markup(params_list_name: str, set: str):
    markup = InlineKeyboardMarkup()
    for name in settings_dict[params_list_name]:
        markup.add(InlineKeyboardButton(name, callback_data=name + '_' + set))
    return markup
# endregion
# region commands


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

        user_sessions = get_user_data(user_id)[2]
        update_row(user_id, 'sessions', user_sessions - 1)
        settings_choice_1(user_id)

    elif is_user_in_table(user_id):
        bot.send_message(user_id, 'вы уже в базе')
        bot.send_message(user_id, 'что вы хотите сделать?', reply_markup=gen_actions_markup())

    else:
        bot.send_message(user_id, 'база переполнена, придется подождать')

# endregion
# region actions callback


@bot.callback_query_handler(func=lambda call: call.data.endswith('new-story'))
def begin_new_story(call):
    user_id = call.message.chat.id
    bot.delete_message(user_id, call.message.message_id)
    user_sessions = get_user_data(user_id)[2]
    if user_sessions > 0:
        update_row(user_id, 'sessions', user_sessions - 1)
        clear_user_story_data(user_id)
        settings_choice_1(user_id)
    else:
        bot.send_message(user_id, 'у вас не осталось сессий')
# endregion
# region settings


def settings_choice_1(user_id):
    bot.send_message(user_id, 'выбери персонажа:', reply_markup=gen_settings_markup('characters_list', 'character'))


@bot.callback_query_handler(func=lambda call: call.data.endswith('character'))
def set_change_1(call):
    user_id = call.message.chat.id
    param = call.data.split('_')[0]
    set = call.data.split('_')[1]
    bot.delete_message(user_id, call.message.message_id)
    update_row(user_id, set, param)
    bot.send_message(user_id, 'герой выбран!')
    settings_choice_2(user_id)


def settings_choice_2(user_id):
    bot.send_message(user_id, 'выбери жанр:', reply_markup=gen_settings_markup('genres_list', 'genre'))


@bot.callback_query_handler(func=lambda call: call.data.endswith('genre'))
def set_change_2(call):
    user_id = call.message.chat.id
    param = call.data.split('_')[0]
    set = call.data.split('_')[1]
    bot.delete_message(user_id, call.message.message_id)
    update_row(user_id, set, param)
    bot.send_message(user_id, 'жанр выбран!')
    settings_choice_3(user_id)


def settings_choice_3(user_id):
    bot.send_message(user_id, 'выбери локацию:', reply_markup=gen_settings_markup('locations_list', 'location'))
    additions_1(user_id)


@bot.callback_query_handler(func=lambda call: call.data.endswith('location'))
def set_change_3(call):
    user_id = call.message.chat.id
    param = call.data.split('_')[0]
    set = call.data.split('_')[1]
    bot.delete_message(user_id, call.message.message_id)
    update_row(user_id, set, param)
    bot.send_message(user_id, 'жанр выбран!')
    additions_1(user_id)


def additions_1(user_id):
    msg = bot.send_message(user_id, 'какие-то дополнения? (напиши "-" если их нет)')
    bot.register_next_step_handler(msg, additions_2)


def additions_2(message: Message):
    user_id = message.chat.id
    if message.text == '-':
        gpt_start(user_id)
    else:
        add_promt = message.text
        update_row(user_id, 'addition', add_promt)
        bot.send_message(user_id, 'я учту это')
        gpt_start(user_id)
# endregion
# region gpt dialogue


def user_request(user_id):
    msg = bot.send_message(user_id, 'как повернет сюжет дальше?')
    bot.register_next_step_handler(msg, dialogue)


def dialogue_start(message: Message):
    user_id = message.chat.id
    text = message.text
    begin = gpt_start(user_id)
    bot.send_message(user_id, begin)

    update_row(user_id, 'story', '')


@bot.message_handler(content_types=['text'])
def dialogue(message):
    user_id = message.chat.id
    text = message.text
    answer = gpt_ask(text, user_id)
    bot.send_message(user_id, answer)
    tokens_num = count_tokens(text)
    bot.send_message(user_id, f'использованные токены: {tokens_num}')
# endregion


bot.infinity_polling()
