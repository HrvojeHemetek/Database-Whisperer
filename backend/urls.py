from django.urls import path
from .views.MainPageView import MainPageView
from .views.MessageView import MessageView
from .views.DBConnectView import DBConnectView
from .views.AudioView import AudioView


urlpatterns = [
    path('', MainPageView.as_view(), name='main_page'),
    path('messages/', MessageView.as_view(), name='message-view'),
    path('db_connect', DBConnectView.as_view(), name='db_connect_view'),
    path('audio',AudioView.as_view(), name='audio'),
]
