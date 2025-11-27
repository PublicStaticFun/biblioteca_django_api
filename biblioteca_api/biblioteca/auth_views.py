from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import ModelSerializer, CharField, ValidationError
from rest_framework.views import APIView

class RegistroSerializer(ModelSerializer):
    password = CharField(write_only=True)
    password2 = CharField(write_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "password2")

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise ValidationError("Las contraseñas no coinciden.")
        if len(data["password"]) < 8:
            raise ValidationError("Contraseña muy corta")
        return data
    
    def create(self, validated_data):
        validated_data.pop("password2")
        return User.objects.create_user(username=validated_data["username"],
                                        email = validated_data.get("email"),
                                        password=validated_data["password"])
    
class RegistroView(generics.CreateAPIView):
    serializer_class = RegistroSerializer
    permission_classes = [permissions.AllowAny]

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)