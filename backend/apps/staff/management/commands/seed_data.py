from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from apps.staff.models import StaffMember, StaffAvailability
from apps.observatory.models import Telescope, Instrument
from apps.shifts.models import Shift, Schedule


class Command(BaseCommand):
    help = 'Seeds the database with sample data for testing'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database...')
        
        # Create Telescopes
        self.stdout.write('Creating telescopes...')
        telescope1, _ = Telescope.objects.get_or_create(
            code='VLT1',
            defaults={
                'name': 'Very Large Telescope 1',
                'aperture': 8.2,
                'description': 'Main observing telescope'
            }
        )
        telescope2, _ = Telescope.objects.get_or_create(
            code='SMAST',
            defaults={
                'name': 'Small Auxiliary Telescope',
                'aperture': 1.5,
                'description': 'Auxiliary telescope for monitoring'
            }
        )
        
        # Create Instruments
        self.stdout.write('Creating instruments...')
        Instrument.objects.get_or_create(
            code='SPEC1',
            defaults={
                'name': 'High Resolution Spectrograph',
                'telescope': telescope1,
                'description': 'Spectroscopy instrument'
            }
        )
        Instrument.objects.get_or_create(
            code='CAM1',
            defaults={
                'name': 'Wide Field Camera',
                'telescope': telescope2,
                'description': 'Imaging camera'
            }
        )
        
        # Create Users and Staff Members
        self.stdout.write('Creating staff members...')
        
        staff_data = [
            {
                'username': 'jdoe',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john.doe@observatory.org',
                'employee_id': 'EMP001',
                'role': 'astronomer',
                'prefers_night_shifts': True,
            },
            {
                'username': 'asmith',
                'first_name': 'Alice',
                'last_name': 'Smith',
                'email': 'alice.smith@observatory.org',
                'employee_id': 'EMP002',
                'role': 'telescope_operator',
                'prefers_night_shifts': True,
            },
            {
                'username': 'bjones',
                'first_name': 'Bob',
                'last_name': 'Jones',
                'email': 'bob.jones@observatory.org',
                'employee_id': 'EMP003',
                'role': 'support_scientist',
                'prefers_night_shifts': False,
            },
            {
                'username': 'cwilson',
                'first_name': 'Carol',
                'last_name': 'Wilson',
                'email': 'carol.wilson@observatory.org',
                'employee_id': 'EMP004',
                'role': 'night_assistant',
                'prefers_night_shifts': True,
            },
        ]
        
        staff_members = []
        for data in staff_data:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'email': data['email'],
                }
            )
            if created:
                user.set_password('password123')
                user.save()
            
            staff, _ = StaffMember.objects.get_or_create(
                user=user,
                defaults={
                    'employee_id': data['employee_id'],
                    'role': data['role'],
                    'prefers_night_shifts': data['prefers_night_shifts'],
                    'hire_date': datetime.now().date() - timedelta(days=365),
                }
            )
            staff_members.append(staff)
        
        # Create some shifts
        self.stdout.write('Creating shifts...')
        today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        for i in range(7):  # Create shifts for next 7 days
            shift_date = today + timedelta(days=i)
            
            # Day shift
            Shift.objects.get_or_create(
                start_time=shift_date.replace(hour=8),
                end_time=shift_date.replace(hour=16),
                defaults={
                    'shift_type': 'day',
                    'assigned_staff': staff_members[i % len(staff_members)],
                    'telescope': telescope1 if i % 2 == 0 else telescope2,
                    'status': 'scheduled',
                    'description': f'Day observations on {shift_date.date()}'
                }
            )
            
            # Night shift
            Shift.objects.get_or_create(
                start_time=shift_date.replace(hour=20),
                end_time=(shift_date + timedelta(days=1)).replace(hour=6),
                defaults={
                    'shift_type': 'night',
                    'assigned_staff': staff_members[(i + 1) % len(staff_members)],
                    'telescope': telescope1,
                    'status': 'scheduled',
                    'description': f'Night observations on {shift_date.date()}'
                }
            )
        
        # Create a schedule
        self.stdout.write('Creating schedule...')
        schedule, _ = Schedule.objects.get_or_create(
            name='Weekly Schedule',
            defaults={
                'description': 'Sample weekly schedule',
                'start_date': today.date(),
                'end_date': (today + timedelta(days=7)).date(),
                'status': 'published',
            }
        )
        schedule.shifts.set(Shift.objects.filter(start_time__gte=today))
        
        self.stdout.write(self.style.SUCCESS('✅ Database seeded successfully!'))
        self.stdout.write(f'Created {len(staff_members)} staff members')
        self.stdout.write(f'Created {Shift.objects.count()} shifts')
        self.stdout.write(f'Created 1 schedule')
