from django.shortcuts import render
from django.contrib.auth import get_user_model
from accounts.serializers import RegisterSerializer
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import authenticate
from rest_framework import (
    viewsets,
    permissions,
    generics,
    response,
    status,
    authentication,
    )
User = get_user_model()

# Create your views here.
class RegisterView(generics.CreateAPIView):
    """The logic here creates a user and returns a token
        that can be used in all authentication required views,
        by overriding the create method.
    """
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)

        return response.Response({
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,

            },
            "token": token.key
        })
    
@api_view(['POST'])
def login(request):
    username=request.data.get('username')
    password=request.data.get('password')

    user = authenticate(username=username, password=password)

    if user:
        token, _ = Token.objects.get_or_create(user=user)

        return response.Response({
            'message': 'Login successful',
            'token': token.key,
        }, status=status.HTTP_200_OK)
    
    return response.Response({
        'message':'Authentication failed',
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@authentication_classes([authentication.TokenAuthentication])
@permission_classes([permissions.IsAuthenticated()])
def logout(request):
    request.user.auth_token.delete()

    return response.Response({
        'message': 'Logged out successfully',

    }, status=status.HTTP_200_OK)
