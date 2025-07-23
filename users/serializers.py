from rest_framework import serializers

from .models import User


class PhoneRequestSerializer(serializers.Serializer):
    phone = serializers.CharField(
        max_length=15
    )


class CodeVerifySerializer(serializers.Serializer):
    phone = serializers.CharField(
        max_length=15
    )
    code = serializers.CharField(
        max_length=4
    )


class UserProfileSerializer(serializers.ModelSerializer):
    referrals = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['phone', 'invite_code', 'activated_invite_code', 'referrals']
        read_only_fields = ['phone', 'invite_code', 'referrals']

    # Получает список пользователей, которые ввели инвайт-код текущего пользователя
    def get_referrals(self, obj):
        referral_users = User.objects.filter(activated_invite_code=obj.invite_code)
        return [user.phone for user in referral_users]


class ActivateInviteCodeSerializer(serializers.Serializer):
    invite_code = serializers.CharField(
        max_length=6
    )
