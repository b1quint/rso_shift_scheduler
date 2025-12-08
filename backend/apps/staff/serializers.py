from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Team, ShiftType, StaffMember, StaffAvailability, DailyAvailability


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
            'id', 'user_data', 'team', 'employee_id', 'role', 'status',
            'phone', 'prefers_night_shifts', 'max_consecutive_nights',
            'min_rest_days', 'hire_date', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        user_data = validated_data.pop('user_data')
        user = User.objects.create(**user_data)
        staff_member = StaffMember.objects.create(user=user, **validated_data)
        return staff_member
    
    def to_representation(self, instance):
        # Use the standard serializer for output
        return StaffMemberSerializer(instance).data


class StaffMemberUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating StaffMember with user fields"""
    # Nested dict for updating user fields (all fields optional for updates)
    # Using DictField without child restriction to support mixed data types
    user_data = serializers.DictField(required=False, allow_null=True)
    
    # Allowed user fields that can be updated
    ALLOWED_USER_FIELDS = {'username', 'email', 'first_name', 'last_name'}
    
    class Meta:
        model = StaffMember
        fields = [
            'id', 'user_data', 'team', 'employee_id', 'role', 'status',
            'phone', 'prefers_night_shifts', 'max_consecutive_nights',
            'min_rest_days', 'hire_date', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def update(self, instance, validated_data):
        user_data = validated_data.pop('user_data', None)
        if user_data:
            # Update only allowed user fields that are provided
            for field, value in user_data.items():
                if field in self.ALLOWED_USER_FIELDS and hasattr(instance.user, field):
                    setattr(instance.user, field, value)
            instance.user.save()
        
        # Update staff member fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
    def to_representation(self, instance):
        # Use the standard serializer for output
        return StaffMemberSerializer(instance).data


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


class DailyAvailabilitySerializer(serializers.ModelSerializer):
    """Serializer for DailyAvailability model"""
    staff_member_name = serializers.CharField(source='staff_member.full_name', read_only=True)
    availability_display = serializers.ReadOnlyField()
    
    class Meta:
        model = DailyAvailability
        fields = [
            'id', 'staff_member', 'staff_member_name', 'date',
            'availability_code', 'availability_display', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
