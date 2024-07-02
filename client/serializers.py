from backstage.models import ChannelModel
from rest_framework import serializers


class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChannelModel
        fields = ['cid', 'channel_code', 'channel_name', 'credit_range']
