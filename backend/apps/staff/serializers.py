from rest_framework import serializers
from django.contrib.auth.models import User
from .models import StaffMember, StaffAvailability


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class StaffMemberSerializer(serializers.ModelSerializer):
    """Serializer for StaffMember model"""
    user = UserSerializer(read_only=True)
    full_name = serializers.ReadOnlyField()
    is_available = serializers.ReadOnlyField()
    
    class Meta:
        model = StaffMember
        fields = [
            'id', 'user', 'employee_id', 'role', 'status', 
            'phone', 'prefers_night_shifts', 'max_consecutive_nights',
            'min_rest_days', 'hire_date', 'notes', 'full_name', 
            'is_available', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class StaffMemberCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating StaffMember with user"""
    user_data = UserSerializer()
    
    class Meta:
        model = StaffMember
        fields = [
            'id', 'user_data', 'employee_id', 'role', 'status',
            'phone', 'prefers_night_shifts', 'max_consecutive_nights',
            'min_rest_days', 'hire_date', 'notes'
        ]
        read_only_fields = ['id']
    
    def create(self, validated_data):
        user_data = validated_data.pop('user_data')
        user = User.objects.create(**user_data)
        staff_member = StaffMember.objects.create(user=user, **validated_data)
        return staff_member


class StaffAvailabilitySerializer(serializers.ModelSerializer):
    """Serializer for StaffAvailability model"""
    staff_member_name = serializers.CharField(source='staff_member.full_name', read_only=True)
    
    class Meta:
        model = StaffAvailability
        fields = [
            'id', 'staff_member', 'staff_member_name', 'start_date',
            'end_date', 'availability_type', 'reason', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
