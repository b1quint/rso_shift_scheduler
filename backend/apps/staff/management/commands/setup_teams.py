"""
Script to populate Teams and ShiftTypes for Vera Rubin Observatory
and migrate existing shift data.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.staff.models import Team, ShiftType, StaffMember
from apps.shifts.models import Shift


class Command(BaseCommand):
    help = 'Setup Vera Rubin Observatory teams and shift types'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('Setting up teams and shift types for Vera Rubin Observatory...')
        
        # Create Teams
        obs_specialists, created = Team.objects.get_or_create(
            code='OBS',
            defaults={
                'name': 'Observing Specialists',
                'description': 'Team responsible for telescope operations and observations'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✓ Created team: {obs_specialists.name}'))
        
        support_scientists, created = Team.objects.get_or_create(
            code='SCI',
            defaults={
                'name': 'Support Scientists',
                'description': 'Scientists providing observation support and data analysis'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✓ Created team: {support_scientists.name}'))
        
        # Create Shift Types for Observing Specialists
        obs_shift_types = [
            {'name': 'Day Shift Lead', 'code': '1', 'color': '#f59e0b', 'sort_order': 1},
            {'name': 'Day Shift', 'code': '2', 'color': '#fbbf24', 'sort_order': 2},
            {'name': 'Late Shift Lead', 'code': '3', 'color': '#4338ca', 'sort_order': 3},
            {'name': 'Late Shift', 'code': '4', 'color': '#6366f1', 'sort_order': 4},
            {'name': 'Training', 'code': 'T', 'color': '#8b5cf6', 'sort_order': 5},
            {'name': 'Backup', 'code': 'B', 'color': '#10b981', 'sort_order': 6},
        ]
        
        for shift_data in obs_shift_types:
            shift_type, created = ShiftType.objects.get_or_create(
                team=obs_specialists,
                code=shift_data['code'],
                defaults={
                    'name': shift_data['name'],
                    'color': shift_data['color'],
                    'sort_order': shift_data['sort_order']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'    ✓ Created shift type: {shift_type.name} ({shift_type.code})'))
        
        # Create Shift Types for Support Scientists
        sci_shift_types = [
            {'name': 'Day Shift', 'code': 'D', 'color': '#f59e0b', 'sort_order': 1},
            {'name': 'Late Night Shift', 'code': 'L', 'color': '#4338ca', 'sort_order': 2},
        ]
        
        for shift_data in sci_shift_types:
            shift_type, created = ShiftType.objects.get_or_create(
                team=support_scientists,
                code=shift_data['code'],
                defaults={
                    'name': shift_data['name'],
                    'color': shift_data['color'],
                    'sort_order': shift_data['sort_order']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'    ✓ Created shift type: {shift_type.name} ({shift_type.code})'))
        
        self.stdout.write(self.style.SUCCESS('\n✓ Successfully set up teams and shift types!'))
