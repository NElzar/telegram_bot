from telegram_bot.settings import URL, API_KEY, KEY_WORD, URL_FOR_SOURCE
from .models import *
import requests


def get_news_from_source(word):
    r = "{url}{url_2}{api_key}".format(url=URL_FOR_SOURCE, url_2=KEY_WORD, api_key=API_KEY)
    result = requests.get(r)
    data = result.json()
    for article in data['sources']:
        name = article['name']
        if name == word:
            content = article['description'] or 'Неизвестный'
            SourceNews.objects.create(content=content)
        else:
            continue


def get_news(word):
    result = requests.get("{url}{word}{key_word}{api_key}".format(url=URL, word=word, key_word=KEY_WORD, api_key=API_KEY))
    data = result.json()
    for article in data['articles']:
        source_url = article['url']
        title = article['title']
        author_name = article['author'] or 'Неизвестный'
        content = article['content'] or 'Неизвестный'
        source_article = article['source'] or 'Неизвестный'
        if News.objects.filter(title=title).exists():
            continue
        source_name = source_article['name'] or 'Неизвестный'
        source, created = Source.objects.get_or_create(name=source_name)
        author = Author.objects.create(name=author_name, source=source)
        News.objects.create(title=title, content=content, link=source_url, author=author)
    return data


def get_news_from_db(keyword, page=1):
    start = 0
    end = 5
    if page == 2:
        start = 5
        end = 10
    if page == 3:
        start = 10
        end = 15
    if page == 4:
        start = 15
        end = 20
    if page == 5:
        start = 20
        end = 25
    readable_list = News.objects.values_list('title', 'link').order_by('-id')[start:end]
    a = ''
    for val in list(readable_list):
        a += ' -- {0}\n <a href="{1}">Источник</a>\n\n'.format(val[0], val[1])
    if not a:
        a = 'Все доступные новости уже получили'
    return a


def get_news_from_db_by_source(source, page=1):
    start = 0
    end = 5
    if page == 2:
        start = 5
        end = 10
    if page == 3:
        start = 10
        end = 15
    if page == 4:
        start = 15
        end = 20
    if page == 5:
        start = 20
        end = 25
    readable_list = News.objects.filter(author__source__name=source).values_list('title', 'link').order_by('-id')[start:end]
    a = ''
    for val in list(readable_list):
        a += ' -- {0}\n <a href="{1}">Источник</a>\n\n'.format(val[0], val[1])
    if not a:
        a = 'Все доступные новости уже получили'
    return a


def delete_all():
    News.objects.all().delete()
    Author.objects.all().delete()
    Source.objects.all().delete()
    TgUserId.objects.all().delete()
    KeyWord.objects.all().delete()
    print('Успешно форматировано')
