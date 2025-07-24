from drf_spectacular.utils import extend_schema_serializer, OpenApiExample, extend_schema_field
from rest_framework import serializers

from .models import User

@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Пример запроса кода',
            value={'phone': '+79123456789'}
        )
    ]
)
class PhoneRequestSerializer(serializers.Serializer):
    phone = serializers.CharField(
        max_length=15
    )

@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Пример проверки кода',
            value={'phone': '+79123456789', 'code': '1234'}
        )
    ]
)
class CodeVerifySerializer(serializers.Serializer):
    phone = serializers.CharField(
        max_length=15
    )
    code = serializers.CharField(
        max_length=4
    )


class UserProfileSerializer(serializers.ModelSerializer):
    @extend_schema_field(serializers.ListField(child=serializers.CharField()))

    def get_referrals(self, obj):
        referral_users = User.objects.filter(activated_invite_code=obj.invite_code)
        return [user.phone for user in referral_users]

    referrals = serializers.SerializerMethodField(
        help_text="Список телефонных номеров пользователей, активировавших инвайт-код данного пользователя"
    )

    class Meta:
        model = User
        fields = ['phone', 'invite_code', 'activated_invite_code', 'referrals']
        read_only_fields = ['phone', 'invite_code', 'referrals']


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Пример активации инвайт-кода',
            value={'invite_code': 'ABC123'}
        )
    ]
)
class ActivateInviteCodeSerializer(serializers.Serializer):
    invite_code = serializers.CharField(
        max_length=6
    )
