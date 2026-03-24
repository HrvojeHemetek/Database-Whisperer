from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from ..models import DBConnect
from ..main_functions.chat_functions import create_new_db_connection

from backend.serializer import DBConnectSerializer

class DBConnectView(APIView):
    def post(self, request):
        serializer = DBConnectSerializer(data=request.data)
        if serializer.is_valid():
            db_type = serializer.validated_data['type']
            result = create_new_db_connection(db_type)
            return Response({'message': "success"}, status=status.HTTP_201_CREATED)
        else:
            return Response("Error", status=status.HTTP_400_BAD_REQUEST)
