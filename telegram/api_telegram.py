import telebot
from .models import KeyWord, TgUserId, Source, News, SourceNews
from .news_api import get_news, get_news_from_db, get_news_from_db_by_source, get_news_from_source
from telebot import types
from telegram_bot_pagination import InlineKeyboardPaginator
from telegram_bot.settings import TELEGRAM_TOKEN, SBER_NUMBER, QIWI_NUMBER
bot = telebot.TeleBot(TELEGRAM_TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    markup = get_markup(message)
    a = 'Выберите что вас интересует или напишите ключевое слово'
    bot.send_message(message.chat.id, a, parse_mode='html', reply_markup=markup)


def get_markup(message):
    telegram_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    keys = KeyWord.objects.filter(tguserid__tg_id=telegram_id).values_list('name', flat=True)
    markup.add(types.KeyboardButton('/создатькнопку'),
               types.KeyboardButton('поддержать разработчика'),
               types.KeyboardButton('/удалитькнопку'),
               types.KeyboardButton('/искатьпоисточнику')
               )

    for button in keys:
        markup.add(types.KeyboardButton(button))
    return markup


@bot.message_handler(commands=['удалитькнопку'])
def delete(message):
    sent = bot.send_message(message.chat.id, 'Нажмите ту кнопку которую хотите удалить', parse_mode='html')
    bot.register_next_step_handler(sent, delete_button)


def delete_button(message):
    telegram_id = message.chat.id
    message_text = message.text.strip().lower()
    keys = KeyWord.objects.filter(tguserid__tg_id=telegram_id, name=message_text).delete()
    bot.send_message(message.chat.id, 'Успешно удалено', parse_mode='html', reply_markup=get_markup(message))


def make_readable_with_id(need_list):
    a = ''
    for val in list(need_list):
        n = 0
        a += '{0} -- {1}\n'.format(val[0], val[1])
    return a


@bot.message_handler(commands=['искатьпоисточнику'])
def get_source(message):
    bot.send_message(message.chat.id, 'Напишите id напротив источника, по которому хотите искать', parse_mode='html')
    source_list = Source.objects.values_list('id', 'name')
    b = make_readable_with_id(source_list)
    sent = bot.send_message(message.chat.id, b, parse_mode='html')
    bot.register_next_step_handler(sent, search_by_source)


@bot.message_handler(content_types=['source'])
def search_by_source(message):
    SourceNews.objects.all().delete()
    message_text = message.text
    readable_message_text = Source.objects.get(id=message_text).name
    get_news_from_source(readable_message_text)
    data = SourceNews.objects.values_list('content')
    a = make_readable(data)
    bot.send_message(message.chat.id, a, parse_mode='html')


def make_readable(need_list):
    a = ''
    for val in list(need_list):
        a += ' -- {0}\n'.format(val[0])
    return a


@bot.message_handler(commands=['создатькнопку'])
def save_chat_id(message):
    tg_id = message.chat.id
    result, created = TgUserId.objects.get_or_create(tg_id=tg_id)
    sent = bot.send_message(message.chat.id, 'Введите слово которое хотите поместить в кнопку', parse_mode='html')
    bot.register_next_step_handler(sent, save_key_word)


@bot.message_handler(content_types=['keyword'])
def save_key_word(message):
    tguserid = TgUserId.objects.get(tg_id=message.chat.id)
    message_text = message.text.strip().lower()
    key_word = KeyWord.objects.create(name=message_text, tguserid=tguserid)
    bot.send_message(message.chat.id, 'Готово!', parse_mode='html', reply_markup=get_markup(message))


@bot.message_handler(commands=['сбербанк'])
def take_sber(message):
    a = SBER_NUMBER
    markup = get_markup(message)
    bot.send_message(message.chat.id, a, parse_mode='html', reply_markup=markup)


@bot.message_handler(commands=['qiwi'])
def take_qiwi(message):
    a = QIWI_NUMBER
    markup = get_markup(message)
    bot.send_message(message.chat.id, a, parse_mode='html', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def get_text(message):
    message_text = message.text.strip().lower()
    try:
        if message_text == 'поддержать разработчика':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
            btn1 = types.KeyboardButton('/сбербанк')
            btn2 = types.KeyboardButton('/qiwi')
            markup.add(btn1, btn2)
            answer = 'Куда вам удобнее будет отправить помощь?'

            bot.send_message(message.chat.id, answer, parse_mode='html', reply_markup=markup)
            return
        else:
            get_news(message_text)
            news = get_news_from_db(message_text)

    except IndexError:
        news = 'По ключевому слову новостей не найдено, либо уже получили все новости на данный момент'
    send_news(message, message_text, by_source=True)


def send_news(message, keyword, page=1, by_source=True):
    paginator = InlineKeyboardPaginator(
        10,
        current_page=page,
        data_pattern='Новости#'+keyword+'#{page}'
    )
    if by_source is not True:
        a = get_news_from_db_by_source(keyword, page)
    else:
        a = get_news_from_db(keyword, page)
    bot.send_message(
        message.chat.id,
        a,
        reply_markup=paginator.markup,
        parse_mode='html',
        disable_web_page_preview=True
    )


@bot.callback_query_handler(func=lambda call: call.data.split('#')[0]=='Новости')
def characters_page_callback(call):
    page = int(call.data.split('#')[2])
    keyword = call.data.split('#')[1]
    bot.delete_message(
        call.message.chat.id,
        call.message.message_id
    )
    send_news(call.message, keyword, page)


def run_telegram_bot():
    print('Бот успешно запущен!')
    bot.polling(none_stop=True)
