from rest_framework import status
from rest_framework.views import APIView

from backend.models import *
from backend.serializer import *

from backend.main_functions.chat_functions import  *
from rest_framework.response import Response

from backend.main_functions.chat_functions import start_chat

class MainPageView(APIView):
    def post(self, request):
        serializer = MainPageSerializer(data=request.data)
        if serializer.is_valid():
            db_type = serializer.validated_data['type']
            result = check_connection(db_type)
            return Response({'message': result}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


