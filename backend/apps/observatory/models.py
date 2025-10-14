from django.db import models


class Telescope(models.Model):
    """
    Represents a telescope at the observatory.
    """
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    aperture = models.DecimalField(max_digits=5, decimal_places=2, help_text="Aperture in meters")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.aperture}m)"


class Instrument(models.Model):
    """
    Represents an instrument that can be attached to a telescope.
    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    telescope = models.ForeignKey(
        Telescope,
        on_delete=models.CASCADE,
        related_name='instruments'
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['telescope', 'name']
    
    def __str__(self):
        return f"{self.name} on {self.telescope.name}"
