import telebot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from data import get_table_data, is_user_in_table, add_new_user, update_row, settings_dict, actions, get_user_data, \
    clear_user_story_data
from config import TOKEN, ADMINS_ID, MAX_USERS, MAX_MODEL_TOKENS, MAX_TOKENS_PER_SESSION
from gpt import gpt_ask, gpt_start, gpt_end

bot = telebot.TeleBot(token=TOKEN)


# region markups
def gen_actions_markup(exceptions=None):
    if exceptions is None:
        exceptions = []
    markup = InlineKeyboardMarkup()
    for action in actions:
        if action not in exceptions:
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
        bot.send_message(user_id, 'у вас нет доступа к этой функции')


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


@bot.callback_query_handler(func=lambda call: call.data == 'new-story')
def begin_new_story(call):
    user_id = call.message.chat.id
    bot.delete_message(user_id, call.message.message_id)
    user_sessions = get_user_data(user_id)[2]
    if user_sessions > 0:
        clear_user_story_data(user_id)
        update_row(user_id, 'sessions', user_sessions - 1)
        settings_choice_1(user_id)
    else:
        bot.send_message(user_id, 'у вас не осталось сессий')


@bot.callback_query_handler(func=lambda call: call.data == 'continue')
def continue_story(call):  # если кончились токены, можно продолжить потратив еще одну сессию
    user_id = call.message.chat.id
    bot.delete_message(user_id, call.message.message_id)
    data = get_user_data(user_id)
    story = data[8]
    tokens = data[3]
    sessions = data[2]
    if tokens - MAX_MODEL_TOKENS < 0 < sessions:
        update_row(user_id, 'sessions', sessions - 1)
        update_row(user_id, 'tokens', MAX_TOKENS_PER_SESSION)
        user_request(user_id)
    elif tokens - MAX_MODEL_TOKENS > 0:
        user_request(user_id)
    else:
        bot.send_message(user_id, 'у вас не осталось сессий')


@bot.callback_query_handler(func=lambda call: call.data == 'end')
def end_story(call):  # историю можно закончить вне зависимости от количества токенов и сессий
    user_id = call.message.chat.id
    bot.delete_message(user_id, call.message.message_id)
    data = get_user_data(user_id)
    tokens = data[3]
    sessions = data[2]
    story = data[-1]

    text = gpt_end(user_id)
    bot.send_message(user_id, text)
    clear_user_story_data(user_id)
    update_row(user_id, 'story', story + text)
    bot.send_message(user_id, 'начать заново?', reply_markup=gen_actions_markup(['continue', 'end']))


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
    bot.send_message(user_id, 'выбери сеттинг:', reply_markup=gen_settings_markup('settings_list', 'setting'))


@bot.callback_query_handler(func=lambda call: call.data.endswith('setting'))
def set_change_3(call):
    user_id = call.message.chat.id
    param = call.data.split('_')[0]
    set = call.data.split('_')[1]
    bot.delete_message(user_id, call.message.message_id)
    update_row(user_id, set, param)
    bot.send_message(user_id, 'сеттинг выбран!')
    additions_1(user_id)


def additions_1(user_id):
    msg = bot.send_message(user_id, 'какие-то дополнения? (напиши "-" если их нет)')
    bot.register_next_step_handler(msg, additions_2)


def additions_2(message: Message):
    user_id = message.chat.id
    if message.text != '-':
        add_promt = message.text
        update_row(user_id, 'addition', add_promt)
        bot.send_message(user_id, 'я учту это')
    dialogue_start(user_id)
# endregion
# region echo message


@bot.message_handler(content_types=['text'])
def echo(message: Message) -> None:
    """Функция ответа на некорректное сообщение от пользователя

    Функция отправляет сообщение с некорректным ответом от пользователя в формате
    'Вы напечатали: *сообщение пользователя*.что?'
    :param message: некорректное сообщение пользователя"""
    bot.send_message(chat_id=message.chat.id, text=f'Вы напечатали: {message.text}. Что?')
# endregion
# region gpt dialogue


def user_request(user_id):
    msg = bot.send_message(user_id, 'как повернет сюжет дальше?')
    bot.register_next_step_handler(msg, dialogue)


def dialogue_start(user_id):
    load_message = bot.send_message(user_id, 'подождите.')
    bot.edit_message_text('подождите..', load_message.chat.id, load_message.message_id)
    begin = gpt_start(user_id)
    tokens_num = begin['tokens']
    text = begin['result']
    bot.edit_message_text('подождите...', load_message.chat.id, load_message.message_id)
    update_row(user_id, 'story', text)
    bot.delete_message(load_message.chat.id, load_message.message_id)
    bot.send_message(user_id, begin['result'])
    bot.send_message(user_id, f'использованные токены: {tokens_num}')
    bot.send_message(user_id, 'что вы хотите сделать сейчас?', reply_markup=gen_actions_markup())


@bot.message_handler(content_types=['text'])
def dialogue(message):
    user_id = message.chat.id
    text = message.text
    user_tokens = get_user_data(user_id)[3]
    if user_tokens - MAX_MODEL_TOKENS > 0:
        story = get_user_data(user_id)[-1]
        answer = gpt_ask(text, user_id)
        update_row(user_id, 'story', story + ' ' + text + ' ' + answer['result'])
        bot.send_message(user_id, answer['result'])
        tokens_num = answer['tokens']
        update_row(user_id, 'tokens', user_tokens - tokens_num)
        bot.send_message(user_id, f'использованные токены: {MAX_TOKENS_PER_SESSION - user_tokens}')
        bot.send_message(user_id, 'что вы хотите сделать сейчас?', reply_markup=gen_actions_markup())
    else:
        bot.send_message(user_id,
                         'у вас закончились токены для этого сюжета, если вы продолжите или закончите сюжет, то начнется новая сессия',
                         reply_markup=gen_actions_markup())
# endregion


bot.infinity_polling()
