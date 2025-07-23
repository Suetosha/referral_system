import time
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import PhoneRequestSerializer, CodeVerifySerializer, UserProfileSerializer, \
    ActivateInviteCodeSerializer
from .auth import generate_verification_code, save_code_to_cache, get_code_from_cache, generate_invite_code
from .models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated


class RequestCodeView(APIView):
    def post(self, request):
        try:
            serializer = PhoneRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            phone = serializer.validated_data['phone']
            code = generate_verification_code()
            save_code_to_cache(phone, code)

            # Эмуляция задержки 2 секунды
            time.sleep(2)

            return Response({'detail': 'Код отправлен', 'debug_code': code}, status=200)
        except Exception as e:
            return Response({'error': str(e)}, status=400)


class VerifyCodeView(APIView):
    def post(self, request):
        try:
            serializer = CodeVerifySerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            phone = serializer.validated_data['phone']
            code = serializer.validated_data['code']
            cached_code = get_code_from_cache(phone)

            if cached_code != code:
                return Response({'detail': 'Неверный код'}, status=400)

            # Если пользователя нет в бд - создаем, в другом случае получаем его из бд
            user, created = User.objects.get_or_create(phone=phone)

            # Если пользователь создан впервые, генерируем инвайт-код
            if created:
                invite_code = generate_invite_code()
                user.invite_code = invite_code
                user.save()

            refresh = RefreshToken.for_user(user)

            # Отправляем refresh и access токены
            return Response(
                {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token)
                },
                status=200
            )
        except Exception as e:
            return Response({'error': str(e)}, status=400)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)


class ActivateInviteCodeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        # Проверяем, не активировал ли пользователь уже инвайт-код
        if user.activated_invite_code:
            return Response({'detail': 'Вы уже активировали инвайт-код'}, status=400)

        serializer = ActivateInviteCodeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        invite_code = serializer.validated_data['invite_code']

        # Проверяем, существует ли такой инвайт-код
        if not User.objects.filter(invite_code=invite_code).exists():
            return Response({'detail': 'Инвайт-код не существует'}, status=400)

        # Проверяем, не пытается ли пользователь активировать свой собственный инвайт-код
        if user.invite_code == invite_code:
            return Response({'detail': 'Вы не можете активировать свой собственный инвайт-код'}, status=400)

        # Активируем инвайт-код
        user.activated_invite_code = invite_code
        user.save()

        return Response({'detail': 'Инвайт-код успешно активирован'})
