from django.db import models


class MessageModel(models.Model):
    content_chain_of_thoughts = models.TextField()
    content_sql = models.TextField()
    content_reply_to_user = models.TextField()
    result_count = models.IntegerField()

    def __str__(self):
        return f"Message with content: {self.content_sql}"
    

class DBConnect(models.Model):
    type = models.CharField(max_length=20)

    def __str__(self):
        return self.db_type

class MainPage(models.Model):
    type = models.CharField(max_length=20)

    def __str__(self):
        return self.type
