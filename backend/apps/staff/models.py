from django.db import models
from django.contrib.auth.models import User


class Team(models.Model):
    """
    Represents a team or department at the observatory.
    Each team can have different shift types and requirements.
    """
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True, help_text="Short code for the team")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Team'
        verbose_name_plural = 'Teams'
    
    def __str__(self):
        return self.name


class ShiftType(models.Model):
    """
    Represents a type of shift specific to a team.
    Different teams can have different shift types with custom codes.
    """
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='shift_types'
    )
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, help_text="Short code displayed in calendar (e.g., D, L, 1, 2)")
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#6b7280', help_text="Hex color code for display")
    
    # Default timing (can be overridden per shift)
    default_start_time = models.TimeField(null=True, blank=True)
    default_end_time = models.TimeField(null=True, blank=True)
    default_duration_hours = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0, help_text="Order for display in lists")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['team', 'sort_order', 'name']
        unique_together = [['team', 'code']]
        verbose_name = 'Shift Type'
        verbose_name_plural = 'Shift Types'
    
    def __str__(self):
        return f"{self.team.name} - {self.name} ({self.code})"


class StaffMember(models.Model):
    """
    Represents a staff member at the observatory.
    Extends the base User model with observatory-specific information.
    """
    ROLE_CHOICES = [
        ('astronomer', 'Astronomer'),
        ('telescope_operator', 'Telescope Operator'),
        ('support_scientist', 'Support Scientist'),
        ('night_assistant', 'Night Assistant'),
        ('day_crew', 'Day Crew'),
        ('maintenance', 'Maintenance'),
        ('admin', 'Administrator'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('on_leave', 'On Leave'),
        ('inactive', 'Inactive'),
    ]
    
    # Link to Django User model
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='staff_profile'
    )
    
    # Team Assignment
    team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='members'
    )
    
    # Staff Information
    employee_id = models.CharField(max_length=20, unique=True)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    phone = models.CharField(max_length=20, blank=True)
    
    # Availability Preferences
    prefers_night_shifts = models.BooleanField(default=False)
    max_consecutive_nights = models.IntegerField(default=5)
    min_rest_days = models.IntegerField(default=2)
    
    # Metadata
    hire_date = models.DateField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['user__last_name', 'user__first_name']
        verbose_name = 'Staff Member'
        verbose_name_plural = 'Staff Members'
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.role})"
    
    @property
    def full_name(self):
        return self.user.get_full_name()
    
    @property
    def is_available(self):
        return self.status == 'active'


class StaffAvailability(models.Model):
    """
    Tracks specific availability windows for staff members.
    Used for vacation, special circumstances, etc.
    """
    AVAILABILITY_TYPE = [
        ('available', 'Available'),
        ('unavailable', 'Unavailable'),
        ('preferred', 'Preferred'),
    ]
    
    staff_member = models.ForeignKey(
        StaffMember,
        on_delete=models.CASCADE,
        related_name='availability_windows'
    )
    
    start_date = models.DateField()
    end_date = models.DateField()
    availability_type = models.CharField(max_length=20, choices=AVAILABILITY_TYPE)
    reason = models.CharField(max_length=200, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['start_date']
        verbose_name = 'Staff Availability'
        verbose_name_plural = 'Staff Availabilities'
    
    def __str__(self):
        return f"{self.staff_member.full_name}: {self.availability_type} ({self.start_date} to {self.end_date})"


class DailyAvailability(models.Model):
    """
    Tracks daily availability status for each staff member.
    - = Not set (default), X = Unavailable, ? = Maybe available (prefer not to assign), A = Available
    """
    AVAILABILITY_CODE_CHOICES = [
        ('-', 'Not Set'),
        ('X', 'Unavailable'),
        ('?', 'Maybe Available (Prefer Not)'),
        ('A', 'Available'),
    ]
    
    staff_member = models.ForeignKey(
        StaffMember,
        on_delete=models.CASCADE,
        related_name='daily_availability'
    )
    date = models.DateField()
    availability_code = models.CharField(
        max_length=1,
        choices=AVAILABILITY_CODE_CHOICES,
        default='-',
        help_text="-=Not Set, X=Unavailable, ?=Maybe Available, A=Available"
    )
    notes = models.CharField(max_length=200, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['date', 'staff_member']
        unique_together = [['staff_member', 'date']]
        verbose_name = 'Daily Availability'
        verbose_name_plural = 'Daily Availabilities'
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['staff_member', 'date']),
        ]
    
    def __str__(self):
        return f"{self.staff_member.full_name} - {self.date}: {self.availability_code}"
    
    @property
    def availability_display(self):
        return self.get_availability_code_display()
