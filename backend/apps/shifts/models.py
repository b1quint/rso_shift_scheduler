from django.db import models
from apps.staff.models import StaffMember
from apps.observatory.models import Telescope


class Shift(models.Model):
    """
    Represents a single shift assignment.
    """
    SHIFT_TYPE_CHOICES = [
        ('day', 'Day Shift'),
        ('night', 'Night Shift'),
        ('twilight', 'Twilight Shift'),
        ('on_call', 'On-Call'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Shift Details
    shift_type = models.CharField(max_length=20, choices=SHIFT_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    
    # Timing
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    
    # Assignment
    assigned_staff = models.ForeignKey(
        StaffMember,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='shifts'
    )
    
    telescope = models.ForeignKey(
        Telescope,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='shifts'
    )
    
    # Additional Information
    description = models.TextField(blank=True)
    notes = models.TextField(blank=True, help_text="Internal notes")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_shifts'
    )
    
    class Meta:
        ordering = ['start_time']
        indexes = [
            models.Index(fields=['start_time', 'end_time']),
            models.Index(fields=['assigned_staff', 'start_time']),
        ]
    
    def __str__(self):
        staff_name = self.assigned_staff.full_name if self.assigned_staff else "Unassigned"
        return f"{self.shift_type} - {staff_name} ({self.start_time.date()})"
    
    @property
    def duration_hours(self):
        """Calculate shift duration in hours"""
        return (self.end_time - self.start_time).total_seconds() / 3600
    
    @property
    def is_night_shift(self):
        """Check if this is a night shift"""
        return self.shift_type == 'night'
    
    def clean(self):
        """Validate that end_time is after start_time"""
        from django.core.exceptions import ValidationError
        if self.end_time <= self.start_time:
            raise ValidationError('End time must be after start time')


class Schedule(models.Model):
    """
    Represents a collection of shifts for a specific time period.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Time Period
    start_date = models.DateField()
    end_date = models.DateField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Relationships
    shifts = models.ManyToManyField(Shift, related_name='schedules', blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_schedules'
    )
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.name} ({self.start_date} to {self.end_date})"
    
    @property
    def total_shifts(self):
        """Count total shifts in this schedule"""
        return self.shifts.count()
    
    def clean(self):
        """Validate that end_date is after start_date"""
        from django.core.exceptions import ValidationError
        if self.end_date <= self.start_date:
            raise ValidationError('End date must be after start date')
