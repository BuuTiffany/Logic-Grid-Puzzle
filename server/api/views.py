from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def hello(request):
    return Response({"message": "Hello from Django!"})

@api_view(['GET'])
def leaderboard(request):
    return Response({"message": "Leaderboard endpoint."})