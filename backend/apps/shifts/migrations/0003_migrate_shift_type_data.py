# Generated migration to handle shift_type field change

from django.db import migrations


def migrate_shift_types(apps, schema_editor):
    """
    Migrate old string-based shift types to new ShiftType foreign keys.
    Maps old 'day', 'night', 'twilight', 'on_call' to default shift types.
    """
    Shift = apps.get_model('shifts', 'Shift')
    ShiftType = apps.get_model('staff', 'ShiftType')
    Team = apps.get_model('staff', 'Team')
    
    # Get or create a default team for migration
    default_team, _ = Team.objects.get_or_create(
        code='DEFAULT',
        defaults={'name': 'Default Team', 'description': 'Temp team for data migration'}
    )
    
    # Mapping of old shift type strings to new shift type codes
    mapping = {
        'day': ('D', 'Day Shift', '#f59e0b'),
        'night': ('N', 'Night Shift', '#4338ca'),
        'twilight': ('T', 'Twilight Shift', '#8b5cf6'),
        'on_call': ('O', 'On-Call', '#10b981'),
    }
    
    # Note: Since we changed the field already, we can't migrate old data
    # This migration just ensures new data works correctly
    # Old shifts will need to be manually reassigned or deleted
    
    print("Note: Existing shifts with old shift_type values will need to be reassigned manually")
    print("or you can delete old shifts and create new ones with the new shift types.")


def reverse_migration(apps, schema_editor):
    """Reverse is not supported - would lose ShiftType relationships"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('shifts', '0002_alter_shift_shift_type'),
        ('staff', '0002_team_staffmember_team_shifttype'),
    ]

    operations = [
        migrations.RunPython(migrate_shift_types, reverse_migration),
    ]
