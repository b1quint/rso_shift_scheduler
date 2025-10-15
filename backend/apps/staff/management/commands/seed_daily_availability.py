"""
Management command to seed daily availability data for existing staff members.
"""
from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
import random
from apps.staff.models import StaffMember, DailyAvailability


class Command(BaseCommand):
    help = 'Seeds daily availability data for staff members'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=14,
            help='Number of days to generate availability for (default: 14)'
        )

    def handle(self, *args, **options):
        days = options['days']
        
        # Clear existing daily availability
        DailyAvailability.objects.all().delete()
        self.stdout.write('Cleared existing daily availability data')
        
        # Get all active staff members
        staff_members = StaffMember.objects.filter(status='active')
        
        if not staff_members.exists():
            self.stdout.write(self.style.ERROR('No active staff members found. Run seed_rubin_data first.'))
            return
        
        # Generate availability for the next X days starting from today
        start_date = datetime.now().date()
        
        created_count = 0
        
        for staff in staff_members:
            # Generate a pattern for each staff member
            # 70% fully available, 20% some unavailable days, 10% some maybe days
            pattern_type = random.choices(['available', 'some_unavailable', 'some_maybe'], weights=[70, 20, 10])[0]
            
            for day_offset in range(days):
                current_date = start_date + timedelta(days=day_offset)
                
                if pattern_type == 'available':
                    # Fully available
                    code = 'A'
                elif pattern_type == 'some_unavailable':
                    # Random unavailable days (about 20% of days)
                    code = random.choices(['A', 'X'], weights=[80, 20])[0]
                else:  # some_maybe
                    # Mix of available and maybe available (about 30% maybe)
                    code = random.choices(['A', '?'], weights=[70, 30])[0]
                
                # Add notes for non-available days
                notes = ''
                if code == 'X':
                    notes = random.choice(['Personal appointment', 'Vacation', 'Medical', 'Family obligation'])
                elif code == '?':
                    notes = random.choice(['Prefer not to work', 'Family event possible', 'Other commitment'])
                
                DailyAvailability.objects.create(
                    staff_member=staff,
                    date=current_date,
                    availability_code=code,
                    notes=notes
                )
                created_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} daily availability records for '
                f'{staff_members.count()} staff members over {days} days'
            )
        )
        
        # Show summary
        self.stdout.write('\nAvailability Code Distribution:')
        for code, label in DailyAvailability.AVAILABILITY_CODE_CHOICES:
            count = DailyAvailability.objects.filter(availability_code=code).count()
            percentage = (count / created_count * 100) if created_count > 0 else 0
            self.stdout.write(f'  {code} ({label}): {count} ({percentage:.1f}%)')
