from rest_framework import serializers

from backstage.models import BackstageUserModel, ChannelModel, OrderModel


class BackstageUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = BackstageUserModel
        fields = ['uid', 'username']


class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChannelModel
        fields = '__all__'


class ChannelCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChannelModel
        fields = ['channel_code', 'channel_name', 'credit_range']


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderModel
        fields = '__all__'
