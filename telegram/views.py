from django.http import JsonResponse
from .models import *
from .news_api import get_news, get_news_from_db, get_news_from_source


def take(request):
    word = request.GET.get('word')
    news = get_news(word)
    return JsonResponse(news, safe=False)


def take_source(request):
    word = request.GET.get('word')
    news = get_news_from_source(word)
    return JsonResponse(news, safe=False)


def take_db(request):
    history = News.objects.all()
    a = []
    for story in history:
        a.append({
            'name': story.title,
            'link': story.link
        })
    return JsonResponse(a, safe=False)


