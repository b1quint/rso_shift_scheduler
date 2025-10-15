from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Team, ShiftType, StaffMember, StaffAvailability


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class TeamSerializer(serializers.ModelSerializer):
    """Serializer for Team model"""
    class Meta:
        model = Team
        fields = ['id', 'name', 'code', 'description', 'is_active']
        read_only_fields = ['id']


class ShiftTypeSerializer(serializers.ModelSerializer):
    """Serializer for ShiftType model"""
    team_name = serializers.CharField(source='team.name', read_only=True)
    
    class Meta:
        model = ShiftType
        fields = [
            'id', 'team', 'team_name', 'name', 'code', 'description',
            'color', 'default_start_time', 'default_end_time',
            'default_duration_hours', 'is_active', 'sort_order'
        ]
        read_only_fields = ['id']


class StaffMemberSerializer(serializers.ModelSerializer):
    """Serializer for StaffMember model"""
    user = UserSerializer(read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True)
    team_code = serializers.CharField(source='team.code', read_only=True)
    full_name = serializers.ReadOnlyField()
    is_available = serializers.ReadOnlyField()
    
    class Meta:
        model = StaffMember
        fields = [
            'id', 'user', 'team', 'team_name', 'team_code', 'employee_id', 
            'role', 'status', 'phone', 'prefers_night_shifts', 
            'max_consecutive_nights', 'min_rest_days', 'hire_date', 
            'notes', 'full_name', 'is_available', 'created_at', 'updated_at'
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
