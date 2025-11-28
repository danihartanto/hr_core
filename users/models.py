from django.db import models

# Create your models here.
# users/models.py

from django.db import models
from django.contrib.auth.models import User # Import user bawaan Django
from employees.models import Employee # Import Model Employee

# Pilihan Level User
USER_LEVEL_CHOICES = (
    ('employee', 'Employee Basic'),
    ('staff', 'HR Staff'),
    ('manager', 'Manager'),
    ('admin', 'System Administrator'),
)

class SystemUser(models.Model):
    # Relasi 1-ke-1 ke model User bawaan Django untuk otentikasi
    user = models.OneToOneField(User, on_delete=models.CASCADE) 
    
    # Relasi 1-ke-1 ke Model Employee
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='system_user')

    # Tambahkan field yang diminta
    level_user = models.CharField(max_length=15, choices=USER_LEVEL_CHOICES, default='employee')
    user_status = models.BooleanField(default=True) # Aktif/Nonaktif

    def __str__(self):
        return f"User: {self.user.username} ({self.employee.name})"