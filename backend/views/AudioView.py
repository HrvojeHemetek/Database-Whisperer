from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from ..main_functions.audio_functions import audio_recognition
from ..serializer import AudioSerializer

class AudioView(APIView):
    def post(self,request):
        serializer = AudioSerializer(data=request.data)
        if serializer.is_valid():
            audio_file = serializer.validated_data['audio']
            response_message = audio_recognition(audio_file)
            return Response(response_message)
                        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)