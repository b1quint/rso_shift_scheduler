from django.contrib import admin
from .models import Telescope, Instrument


@admin.register(Telescope)
class TelescopeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'aperture', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'code']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Instrument)
class InstrumentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'telescope', 'is_active']
    list_filter = ['telescope', 'is_active']
    search_fields = ['name', 'code']
    readonly_fields = ['created_at', 'updated_at']
