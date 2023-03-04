from rest_framework import views
from rest_framework.views import Response, APIView


class AuthView(APIView):

    def get(self, request):
        return Response(200)


class PostsView(views.APIView, APIView):

    def post(self, request):
        return Response(status=201)