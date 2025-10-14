from django.contrib import admin
from .models import StaffMember, StaffAvailability


@admin.register(StaffMember)
class StaffMemberAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'employee_id', 'role', 'status', 'hire_date']
    list_filter = ['role', 'status', 'prefers_night_shifts']
    search_fields = ['user__first_name', 'user__last_name', 'employee_id', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'employee_id', 'phone')
        }),
        ('Role & Status', {
            'fields': ('role', 'status', 'hire_date')
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
