from djoser.serializers import UserSerializer
from .models import User, Subscribe
from django.shortcuts import get_object_or_404
from rest_framework import serializers


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, target_user):
        if self.context['request'].user.is_anonymous:
            return False
        return Subscribe.objects.filter(user=self.context['request'].user, author=target_user).exists()

