from django.db import models
from django.contrib.auth.models import User


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
