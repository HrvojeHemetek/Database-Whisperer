from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from backend.models import *
from backend.serializer import *

from backend.main_functions.message_functions import *
from backend.main_functions.Message import *



class MessageView(APIView):
    serializer_class = MessageSerializer


    def post(self,request):
        command = request.data.get('message')
        
        if not command:
            return Response({'error': 'No message provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            response_message = interpret_message(command)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        return Response(response_message, status=status.HTTP_201_CREATED)
