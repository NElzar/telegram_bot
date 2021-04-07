from django.db import models


class Source(models.Model):
    name = models.CharField(max_length=250)


class Author(models.Model):
    name = models.CharField(max_length=250)
    source = models.ForeignKey(Source, on_delete=models.CASCADE)


class SourceNews(models.Model):
    content = models.TextField()
    link = models.URLField()


class News(models.Model):
    title = models.CharField(max_length=250)
    content = models.TextField()
    link = models.URLField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE)


class TgUserId(models.Model):
    tg_id = models.CharField(max_length=250)


class KeyWord(models.Model):
    name = models.CharField(max_length=250)
    tguserid = models.ForeignKey(TgUserId, on_delete=models.CASCADE)


class ChatsMessage(models.Model):
    text = models.CharField(max_length=250)
