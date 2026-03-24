from rest_framework import serializers
from rest_framework.serializers import FileField, Serializer
from .models import *


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageModel
        fields = ['id', 'content_chain_of_thoughts', 'content_sql', 'content_reply_to_user', 'result_count']


class DBConnectSerializer(serializers.ModelSerializer):
    class Meta:
        model = DBConnect
        fields = ['type']

class MainPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MainPage
        fields = ['type']


class AudioSerializer(serializers.Serializer):
    audio = FileField()
    class Meta:
        fields = ['audio']


