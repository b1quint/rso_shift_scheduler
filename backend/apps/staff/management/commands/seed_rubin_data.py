"""
Seed data for Vera Rubin Observatory - Creates realistic staff and shifts
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from apps.staff.models import Team, ShiftType, StaffMember
from apps.shifts.models import Shift
from apps.observatory.models import Telescope
from datetime import datetime, timedelta, time
from django.utils import timezone


class Command(BaseCommand):
    help = 'Seed database with Vera Rubin Observatory data'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('Seeding Vera Rubin Observatory data...\n')
        
        # Get teams
        obs_team = Team.objects.get(code='OBS')
        sci_team = Team.objects.get(code='SCI')
        
        # Create Observing Specialists
        obs_specialists_data = [
            {'first': 'Sarah', 'last': 'Johnson', 'email': 'sarah.johnson@lsst.org', 'emp_id': 'OBS001'},
            {'first': 'Michael', 'last': 'Chen', 'email': 'michael.chen@lsst.org', 'emp_id': 'OBS002'},
            {'first': 'Emily', 'last': 'Rodriguez', 'email': 'emily.rodriguez@lsst.org', 'emp_id': 'OBS003'},
            {'first': 'David', 'last': 'Kim', 'email': 'david.kim@lsst.org', 'emp_id': 'OBS004'},
            {'first': 'Jessica', 'last': 'Williams', 'email': 'jessica.williams@lsst.org', 'emp_id': 'OBS005'},
            {'first': 'Robert', 'last': 'Martinez', 'email': 'robert.martinez@lsst.org', 'emp_id': 'OBS006'},
        ]
        
        for staff_data in obs_specialists_data:
            user, created = User.objects.get_or_create(
                username=staff_data['email'].split('@')[0],
                defaults={
                    'first_name': staff_data['first'],
                    'last_name': staff_data['last'],
                    'email': staff_data['email']
                }
            )
            if created:
                staff, _ = StaffMember.objects.get_or_create(
                    user=user,
                    defaults={
                        'team': obs_team,
                        'employee_id': staff_data['emp_id'],
                        'role': 'telescope_operator',
                        'status': 'active',
                        'hire_date': datetime.now().date() - timedelta(days=365),
                        'phone': f'+1-520-555-{staff_data["emp_id"][-4:]}'
                    }
                )
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created Observing Specialist: {staff.full_name}'))
        
        # Create Support Scientists
        scientists_data = [
            {'first': 'Dr. James', 'last': 'Anderson', 'email': 'james.anderson@lsst.org', 'emp_id': 'SCI001'},
            {'first': 'Dr. Lisa', 'last': 'Thompson', 'email': 'lisa.thompson@lsst.org', 'emp_id': 'SCI002'},
            {'first': 'Dr. Daniel', 'last': 'Garcia', 'email': 'daniel.garcia@lsst.org', 'emp_id': 'SCI003'},
            {'first': 'Dr. Maria', 'last': 'Lopez', 'email': 'maria.lopez@lsst.org', 'emp_id': 'SCI004'},
        ]
        
        for staff_data in scientists_data:
            user, created = User.objects.get_or_create(
                username=staff_data['email'].split('@')[0],
                defaults={
                    'first_name': staff_data['first'],
                    'last_name': staff_data['last'],
                    'email': staff_data['email']
                }
            )
            if created:
                staff, _ = StaffMember.objects.get_or_create(
                    user=user,
                    defaults={
                        'team': sci_team,
                        'employee_id': staff_data['emp_id'],
                        'role': 'support_scientist',
                        'status': 'active',
                        'hire_date': datetime.now().date() - timedelta(days=730),
                        'phone': f'+1-520-555-{staff_data["emp_id"][-4:]}'
                    }
                )
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created Support Scientist: {staff.full_name}'))
        
        # Create telescope
        telescope, created = Telescope.objects.get_or_create(
            code='LSST',
            defaults={
                'name': 'Vera C. Rubin Observatory',
                'aperture': 8.4,
                'is_active': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✓ Created telescope: {telescope.name}'))
        
        # Create shifts for next 14 days
        start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        obs_staff = list(StaffMember.objects.filter(team=obs_team))
        sci_staff = list(StaffMember.objects.filter(team=sci_team))
        
        # Get shift types
        day_lead = ShiftType.objects.get(team=obs_team, code='1')
        day_shift = ShiftType.objects.get(team=obs_team, code='2')
        late_lead = ShiftType.objects.get(team=obs_team, code='3')
        late_shift = ShiftType.objects.get(team=obs_team, code='4')
        sci_day = ShiftType.objects.get(team=sci_team, code='D')
        sci_late = ShiftType.objects.get(team=sci_team, code='L')
        
        shifts_created = 0
        for day in range(14):
            current_date = start_date + timedelta(days=day)
            
            # Observing Specialists shifts (rotate through staff)
            obs_day_idx = (day * 2) % len(obs_staff)
            obs_late_idx = (day * 2 + 1) % len(obs_staff)
            
            # Day Shift Lead (8am-4pm)
            Shift.objects.create(
                shift_type=day_lead,
                assigned_staff=obs_staff[obs_day_idx],
                telescope=telescope,
                start_time=timezone.make_aware(datetime.combine(current_date, time(8, 0))),
                end_time=timezone.make_aware(datetime.combine(current_date, time(16, 0))),
                status='scheduled'
            )
            
            # Day Shift (8am-4pm)
            Shift.objects.create(
                shift_type=day_shift,
                assigned_staff=obs_staff[(obs_day_idx + 1) % len(obs_staff)],
                telescope=telescope,
                start_time=timezone.make_aware(datetime.combine(current_date, time(8, 0))),
                end_time=timezone.make_aware(datetime.combine(current_date, time(16, 0))),
                status='scheduled'
            )
            
            # Late Shift Lead (4pm-midnight)
            Shift.objects.create(
                shift_type=late_lead,
                assigned_staff=obs_staff[obs_late_idx],
                telescope=telescope,
                start_time=timezone.make_aware(datetime.combine(current_date, time(16, 0))),
                end_time=timezone.make_aware(datetime.combine(current_date, time(23, 59))),
                status='scheduled'
            )
            
            # Late Shift (4pm-midnight)
            Shift.objects.create(
                shift_type=late_shift,
                assigned_staff=obs_staff[(obs_late_idx + 1) % len(obs_staff)],
                telescope=telescope,
                start_time=timezone.make_aware(datetime.combine(current_date, time(16, 0))),
                end_time=timezone.make_aware(datetime.combine(current_date, time(23, 59))),
                status='scheduled'
            )
            
            # Support Scientists shifts (rotate through scientists)
            sci_idx = day % len(sci_staff)
            
            # Support Scientist Day Shift (9am-5pm)
            Shift.objects.create(
                shift_type=sci_day,
                assigned_staff=sci_staff[sci_idx],
                telescope=telescope,
                start_time=timezone.make_aware(datetime.combine(current_date, time(9, 0))),
                end_time=timezone.make_aware(datetime.combine(current_date, time(17, 0))),
                status='scheduled'
            )
            
            # Support Scientist Late Night Shift (5pm-1am next day)
            next_day = current_date + timedelta(days=1)
            Shift.objects.create(
                shift_type=sci_late,
                assigned_staff=sci_staff[(sci_idx + 1) % len(sci_staff)],
                telescope=telescope,
                start_time=timezone.make_aware(datetime.combine(current_date, time(17, 0))),
                end_time=timezone.make_aware(datetime.combine(next_day, time(1, 0))),
                status='scheduled'
            )
            
            shifts_created += 6
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Created {shifts_created} shifts for the next 14 days'))
        self.stdout.write(self.style.SUCCESS('✓ Successfully seeded Vera Rubin Observatory data!'))
