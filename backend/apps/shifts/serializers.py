from rest_framework import serializers
from .models import Shift, Schedule
from apps.staff.serializers import StaffMemberSerializer
from apps.observatory.serializers import TelescopeListSerializer


class ShiftSerializer(serializers.ModelSerializer):
    """Serializer for Shift model"""
    assigned_staff_details = StaffMemberSerializer(source='assigned_staff', read_only=True)
    telescope_details = TelescopeListSerializer(source='telescope', read_only=True)
    duration_hours = serializers.ReadOnlyField()
    is_night_shift = serializers.ReadOnlyField()
    
    class Meta:
        model = Shift
        fields = [
            'id', 'shift_type', 'status', 'start_time', 'end_time',
            'assigned_staff', 'assigned_staff_details', 'telescope',
            'telescope_details', 'description', 'notes', 'duration_hours',
            'is_night_shift', 'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']


class ShiftListSerializer(serializers.ModelSerializer):
    """Simplified serializer for shift lists"""
    staff_name = serializers.CharField(source='assigned_staff.full_name', read_only=True)
    telescope_name = serializers.CharField(source='telescope.name', read_only=True)
    
    class Meta:
        model = Shift
        fields = [
            'id', 'shift_type', 'status', 'start_time', 'end_time',
            'assigned_staff', 'staff_name', 'telescope', 'telescope_name',
            'duration_hours'
        ]


class ScheduleSerializer(serializers.ModelSerializer):
    """Serializer for Schedule model"""
    shifts_details = ShiftListSerializer(source='shifts', many=True, read_only=True)
    total_shifts = serializers.ReadOnlyField()
    
    class Meta:
        model = Schedule
        fields = [
            'id', 'name', 'description', 'start_date', 'end_date',
            'status', 'shifts', 'shifts_details', 'total_shifts',
            'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']


class ScheduleListSerializer(serializers.ModelSerializer):
    """Simplified serializer for schedule lists"""
    total_shifts = serializers.ReadOnlyField()
    
    class Meta:
        model = Schedule
        fields = [
            'id', 'name', 'start_date', 'end_date', 'status', 'total_shifts'
        ]
