from django.contrib import admin
from .models import Shift, Schedule


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ['start_time', 'shift_type', 'assigned_staff', 'telescope', 'status']
    list_filter = ['shift_type', 'status', 'telescope', 'start_time']
    search_fields = ['assigned_staff__user__first_name', 'assigned_staff__user__last_name', 'description']
    date_hierarchy = 'start_time'
    readonly_fields = ['created_at', 'updated_at', 'duration_hours']
    
    fieldsets = (
        ('Shift Details', {
            'fields': ('shift_type', 'status', 'start_time', 'end_time', 'duration_hours')
        }),
        ('Assignment', {
            'fields': ('assigned_staff', 'telescope')
        }),
        ('Information', {
            'fields': ('description', 'notes')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'status', 'total_shifts']
    list_filter = ['status', 'start_date']
    search_fields = ['name', 'description']
    date_hierarchy = 'start_date'
    readonly_fields = ['created_at', 'updated_at', 'total_shifts']
    filter_horizontal = ['shifts']
    
    fieldsets = (
        ('Schedule Information', {
            'fields': ('name', 'description', 'status')
        }),
        ('Time Period', {
            'fields': ('start_date', 'end_date')
        }),
        ('Shifts', {
            'fields': ('shifts', 'total_shifts')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )
