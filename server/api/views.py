from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def hello(request):
    return Response({"message": "Hello from Django!"})

@api_view(['GET'])
def getLeaderboard(request):
    return Response({"message": "Leaderboard endpoint."})

@api_view(['GET'])
def getPuzzle(request):
    return Response({"message": "Puzzle endpoint."})

@api_view(['GET'])
def getHint(request):
    return Response({"message": "Hint endpoint."})