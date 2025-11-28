# organization/models.py
from django.db import models

# 1. Company (Level Tertinggi)
class Company(models.Model):
    name = models.CharField(max_length=100, unique=True)
    legal_name = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
        
# 2. Group Head
class GroupHead(models.Model):
    name = models.CharField(max_length=100)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='group_heads')
    
    class Meta:
        unique_together = ('name', 'company')

    def __str__(self):
        return f"{self.name} ({self.company.name})"

# 3. Department (Departemen)
class Department(models.Model):
    name = models.CharField(max_length=100)
    group_head = models.ForeignKey(GroupHead, on_delete=models.CASCADE, related_name='departments')
    
    class Meta:
        unique_together = ('name', 'group_head')

    def __str__(self):
        return f"{self.name} - Group: {self.group_head.name}"

# 4. Unit (Tim/Divisi)
class Unit(models.Model):
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='units')

    class Meta:
        unique_together = ('name', 'department')

    def __str__(self):
        return f"{self.name} ({self.department.name})"

# 5. Job Title / Jabatan (Routing)
JOB_LEVEL_CHOICES = (
    (1, 'Level 1 (Band 1)'),
    (2, 'Level 2 (Band 2)'),
    (3, 'Level 3 (Band 3)'),
    (4, 'Level 4 (Band 4)'),
    (5, 'Level 5 (Band 5) - Staff'),
    (6, 'Level 6 (Band 6) - Non Staff'), # Level terendah
)
class JobTitle(models.Model):
    title_name = models.CharField(max_length=100) 
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='job_titles')
    # level = models.IntegerField(default=1) 
    # LEVEL FIELD DIMODIFIKASI
    level = models.IntegerField(
        choices=JOB_LEVEL_CHOICES, # Menggunakan pilihan statis
        default=6,                 # Default Level 6 (Non-Staff)
        verbose_name='Employee Grade Level'
    )
    level_name = models.CharField(max_length=100,null=True) 

    class Meta:
        unique_together = ('title_name', 'unit')
        
    def __str__(self):
        # Menampilkan Level/Band di representasi string
        return f"Band {self.level} - {self.title_name} {self.get_level_display()} di Unit {self.unit.name}"