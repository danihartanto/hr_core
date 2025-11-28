# employees/models.py

from django.db import models
# Import Model dari aplikasi 'organization'
from organization.models import JobTitle
from datetime import date, timedelta

def one_year_from_today():
    return date.today() + timedelta(days=365)

GENDER_CHOICES = (
    ('LK', 'Laki-laki'),
    ('PR', 'Perempuan'),
    ('OX', 'Lainnya'),
)

RELIGION_CHOICES = (
    ('IS', 'Islam'),
    ('KR', 'Kristen Protestan'),
    ('KA', 'Katolik'),
    ('HI', 'Hindu'),
    ('BU', 'Buddha'),
    ('KO', 'Konghucu'),
    ('LA', 'Lainnya'),
)
class Employee(models.Model):
    
    name = models.CharField(max_length=100)
    employee_id = models.CharField(max_length=20, unique=True)
    # Tambahkan ForeignKey ke JobTitle
    # Ini menentukan posisi karyawan dalam hierarki organisasi
    job_title = models.ForeignKey(
        JobTitle, 
        on_delete=models.SET_NULL, # Jaga data karyawan jika JobTitle dihapus
        null=True, 
        # blank=True,
        related_name='employees'
    )
    # Field Gender Baru
    gender = models.CharField(
        max_length=2, 
        choices=GENDER_CHOICES, 
        default='LK',
        verbose_name='Gender of employee'
    )
    
    # Field Religion Baru
    religion = models.CharField(
        max_length=2,
        choices=RELIGION_CHOICES,
        default='LA',
        verbose_name='Religion of employee'
    )
    # email = models.CharField(max_length=50,null=False)
    email = models.EmailField(max_length=50,unique=True, null=False, blank=True)
    telepon = models.CharField(max_length=50,null=True)
    born_place = models.CharField(max_length=150, null=True)
    born_date = models.DateField(default=date.today)
    hire_date = models.DateField()
    terminate_date = models.DateField(default=one_year_from_today)
    # salary = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        # formatted_salary = "{:,.0f}".format(self.salary).replace(',', '.')
        return f"{self.employee_id} - {self.name}"
        # return f"{self.name} (ID: {self.employee_id}) - Gaji: Rp {formatted_salary}"
        # return self.name
