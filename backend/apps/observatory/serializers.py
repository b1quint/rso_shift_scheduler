from rest_framework import serializers
from .models import Telescope, Instrument


class InstrumentSerializer(serializers.ModelSerializer):
    """Serializer for Instrument model"""
    telescope_name = serializers.CharField(source='telescope.name', read_only=True)
    
    class Meta:
        model = Instrument
        fields = [
            'id', 'name', 'code', 'telescope', 'telescope_name',
            'description', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TelescopeSerializer(serializers.ModelSerializer):
    """Serializer for Telescope model"""
    instruments = InstrumentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Telescope
        fields = [
            'id', 'name', 'code', 'aperture', 'description',
            'is_active', 'instruments', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TelescopeListSerializer(serializers.ModelSerializer):
    """Simplified serializer for telescope lists"""
    class Meta:
        model = Telescope
        fields = ['id', 'name', 'code', 'aperture', 'is_active']
