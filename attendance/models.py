from django.db import models
from employees.models import Employee # Import dari apps employees
from datetime import time,timedelta

# --- Pilihan Tipe Cuti ---
LEAVE_TYPE_CHOICES = (
    ('AL', 'Annual Leave (Cuti Tahunan)'),
    ('SL', 'Sick Leave (Cuti Sakit)'),
    ('ML', 'Maternity Leave (Cuti Melahirkan)'),
    ('UL', 'Unpaid Leave (Cuti Tanpa Bayaran)'),
    ('ER', 'Emergency Leave (Cuti Darurat)'),
)

# --- Pilihan Status Cuti ---
LEAVE_STATUS_CHOICES = (
    ('P', 'Pending'),
    ('A', 'Approved'),
    ('R', 'Rejected'),
)

class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    is_late = models.BooleanField(default=False)
    total_hours = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0,
        verbose_name='Total Jam Kerja Net'
    )
    
    class Meta:
        # Setiap karyawan hanya boleh punya satu record absensi per hari
        unique_together = ('employee', 'date')

    def __str__(self):
        return f"Absensi {self.employee.name} pada {self.date}"
    def save(self, *args, **kwargs):
        # 1. Logika Keterlambatan (Tetap Sama)
        LATE_TIME = time(7, 30, 0)
        if self.check_in:
            self.is_late = self.check_in > LATE_TIME
        else:
            self.is_late = False

        # 2. Logika Perhitungan Total Jam Kerja
        if self.check_in and self.check_out:
            # Menggabungkan tanggal (self.date) dengan waktu untuk membuat datetime object
            # Ini diperlukan agar kita bisa menghitung selisih waktu (timedelta)
            check_in_dt = models.DateTimeField().to_python(f'{self.date} {self.check_in}')
            check_out_dt = models.DateTimeField().to_python(f'{self.date} {self.check_out}')

            # Pastikan check_out setelah check_in (untuk kasus normal)
            if check_out_dt > check_in_dt:
                duration = check_out_dt - check_in_dt
                
                # Kurangi 1 jam (timedelta) untuk istirahat siang
                BREAK_TIME = timedelta(hours=1)
                net_duration = duration - BREAK_TIME
                
                # Konversi total durasi (detik) menjadi jam (Decimal)
                total_hours_in_seconds = net_duration.total_seconds()
                
                # Pastikan total jam tidak negatif
                if total_hours_in_seconds > 0:
                    self.total_hours = round(total_hours_in_seconds / 3600, 2)
                else:
                    self.total_hours = 0
            else:
                self.total_hours = 0 # Durasi tidak valid
        else:
            self.total_hours = 0 # Data check_in/out belum lengkap

        # Panggil metode save() asli
        super().save(*args, **kwargs)

class LeaveRequest(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_requests')
    start_date = models.DateField()
    end_date = models.DateField()
    leave_type = models.CharField(max_length=2, choices=LEAVE_TYPE_CHOICES)
    reason = models.TextField()
    status = models.CharField(max_length=1, choices=LEAVE_STATUS_CHOICES, default='P')
    approved_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_leaves')
    
    # Jumlah hari cuti yang diminta
    days_requested = models.DecimalField(max_digits=3, decimal_places=1)

    def __str__(self):
        return f"Cuti {self.employee.name} dari {self.start_date} s/d {self.end_date}"

class NationalHoliday(models.Model):
    date = models.DateField(unique=True)
    name = models.CharField(max_length=100)
    is_national = models.BooleanField(default=True) # Untuk membedakan cuti bersama atau libur lokal

    def __str__(self):
        return f"Libur: {self.name} ({self.date})"