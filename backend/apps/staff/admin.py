from django.contrib import admin
from .models import Team, ShiftType, StaffMember, StaffAvailability, DailyAvailability


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'code', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Team Information', {
            'fields': ('name', 'code', 'description', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ShiftType)
class ShiftTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'team', 'color', 'is_active', 'sort_order']
    list_filter = ['team', 'is_active']
    search_fields = ['name', 'code', 'description', 'team__name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Shift Type Information', {
            'fields': ('team', 'name', 'code', 'description', 'color', 'is_active', 'sort_order')
        }),
        ('Default Timing', {
            'fields': ('default_start_time', 'default_end_time', 'default_duration_hours')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(StaffMember)
class StaffMemberAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'employee_id', 'role', 'status', 'team', 'hire_date']
    list_filter = ['role', 'status', 'team', 'prefers_night_shifts']
    search_fields = ['user__first_name', 'user__last_name', 'employee_id', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'employee_id', 'phone')
        }),
        ('Team & Role', {
            'fields': ('team', 'role', 'status', 'hire_date')
        }),
        ('Availability Preferences', {
            'fields': ('prefers_night_shifts', 'max_consecutive_nights', 'min_rest_days')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(StaffAvailability)
class StaffAvailabilityAdmin(admin.ModelAdmin):
    list_display = ['staff_member', 'availability_type', 'start_date', 'end_date', 'reason']
    list_filter = ['availability_type', 'start_date']
    search_fields = ['staff_member__user__first_name', 'staff_member__user__last_name', 'reason']
    date_hierarchy = 'start_date'


@admin.register(DailyAvailability)
class DailyAvailabilityAdmin(admin.ModelAdmin):
    list_display = ['staff_member', 'date', 'availability_code', 'notes']
    list_filter = ['availability_code', 'date']
    search_fields = ['staff_member__user__first_name', 'staff_member__user__last_name', 'notes']
    date_hierarchy = 'date'
    readonly_fields = ['created_at', 'updated_at']
