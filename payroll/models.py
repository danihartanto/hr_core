from django.db import models
from employees.models import Employee # Import dari apps employees
from decimal import Decimal
from django.utils import timezone
from django.core.validators import MinValueValidator

# --- Pilihan Status Pembayaran ---
PAYMENT_STATUS_CHOICES = (
    ('Pending', 'Pending'),
    ('Ready', 'Ready for Payment'),
    ('Settled', 'Settled'),
    ('Canceled', 'Canceled'),
)
TYPE_SALARYS = (
    ('GAJI', 'Gaji Bulanan'),
    ('BONUS', 'Bonus Target'),
    ('THR', 'Tunjangan Hari Raya'),
    ('KOMPENSASI','Bonus Kompensasi'),
    ('TTK','Tunjangan Tidak Tetap')
)

class Overtime(models.Model):
    # Karyawan yang melakukan lembur
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='overtimes')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    duration_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0) # Durasi dihitung otomatis
    rate_multiplier = models.DecimalField(max_digits=3, decimal_places=1, default=1.5) # Misal: 1.5x, 2.0x
    is_approved = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Lembur {self.employee.name} pada {self.date}"


class PayrollRecord(models.Model):
    # Karyawan yang menerima gaji
    # --- IDENTITAS PERIODE GAJI ---
    
    employee = models.ForeignKey(
        Employee, 
        on_delete=models.PROTECT, 
        related_name='payroll_records',
        verbose_name="Karyawan"
    )
    salary_type = models.CharField(
        max_length=15, 
        choices=TYPE_SALARYS, 
        default='GAJI', 
        verbose_name="Tipe Gaji"
    )
    
    pay_year = models.PositiveSmallIntegerField(verbose_name="Tahun Gaji")
    pay_month = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)], 
        verbose_name="Bulan Gaji"
    )
    
    # --- RELASI BARU KE PROFIL GAJI ---
    # Mencatat profil gaji mana yang digunakan untuk perhitungan bulan ini
    salary_profile_used = models.ForeignKey(
        'EmployeeSalaryProfile', 
        on_delete=models.PROTECT,
        related_name='payroll_usages',
        verbose_name="Profil Gaji yang Digunakan"
    )
    
    # --- KOMPONEN INPUT TAMBAHAN (HANYA YANG BERSIFAT VARIABEL) ---
    
    # Lembur (Overtime) - Bersifat variabel
    overtime_pay = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0.00'), 
        verbose_name="Bayaran Lembur"
    )

    # Potongan Lain-lain - Bersifat variabel
    other_deductions = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0.00'), 
        verbose_name="Potongan Lain-lain (Variabel)"
    )

    # --- KOMPONEN GAJI DIKUNCI (DIAMBIL DARI PROFILE UNTUK AUDIT) ---
    # Kita tetap menyimpan nilai ini untuk audit, tetapi diisi oleh logika save()
    
    locked_basic_salary = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0.00'), 
        verbose_name="Gaji Pokok Terkunci"
    )
    
    locked_allowances = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0.00'), 
        verbose_name="Tunjangan Terkunci"
    )
    
    locked_deductions = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0.00'), 
        verbose_name="Potongan Tetap Terkunci"
    )

    # Potongan Pajak & BPJS (juga terkunci untuk audit)
    tax_deduction = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0.00'), 
        verbose_name="Potongan PPh 21"
    )
    
    bpjs_deduction = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0.00'), 
        verbose_name="Potongan BPJS"
    )
    
    # --- HASIL AKHIR ---
    
    gross_salary = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0.00'), 
        verbose_name="Gaji Kotor"
    )
    
    net_salary = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0.00'), 
        verbose_name="Gaji Bersih"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Dibuat Pada")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Diperbarui Pada")
    
    payment_status = models.CharField(
        max_length=15, 
        choices=PAYMENT_STATUS_CHOICES, 
        default='Pending', 
        verbose_name="Status Pembayaran"
    )
    
    # ... (Status, Tipe, created_at, updated_at tetap sama) ...

    # --- Logika Otomatis: Perhitungan Gaji dan Penarikan Data ---
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        
        # 1. Tarik data dari EmployeeSalaryProfile saat record baru dibuat
        if is_new and self.employee:
            try:
                # Ambil profil gaji yang AKTIF (asumsi hanya 1 yang aktif per karyawan)
                profile = self.employee.salary_profile 
                
                # Kunci nilai dari profil ke record gaji (PENTING untuk audit)
                self.salary_profile_used = profile
                self.locked_basic_salary = profile.monthly_basic_salary
                self.locked_allowances = profile.total_allowances
                self.locked_deductions = profile.total_deductions
                
            except EmployeeSalaryProfile.DoesNotExist:
                # Tangani jika karyawan belum memiliki profil gaji
                pass

        # 2. Perhitungan Gross Salary (Gaji Kotor)
        total_pemasukan = (
            self.locked_basic_salary + 
            self.locked_allowances + 
            self.overtime_pay
        )
        self.gross_salary = total_pemasukan
        
        # 3. Perhitungan Net Salary (Gaji Bersih)
        total_potongan = (
            self.tax_deduction + 
            self.bpjs_deduction + 
            self.locked_deductions + # Potongan Tetap
            self.other_deductions    # Potongan Variabel
        )
        self.net_salary = self.gross_salary - total_potongan
        
        super().save(*args, **kwargs)
    def __str__(self):
        # Format gaji bersih agar mudah dibaca (misalnya, 10.500.000)
        try:
            formatted_net_salary = "{:,.0f}".format(self.net_salary).replace(',', '.') 
        except Exception:
            # Fallback jika net_salary belum dihitung atau null
            formatted_net_salary = "N/A"
            
        # Mengembalikan kombinasi periode, nama karyawan, dan gaji bersih
        return (
            f"Slip Gaji {self.pay_month}/{self.pay_year} "
            f"(Bersih: Rp {formatted_net_salary} - {self.employee})"
        )


# Status Profil Gaji

from .models import PayrollRecord
SALARY_STATUS_CHOICES = (
    ('ACTTIVE', 'Aktif'),
    ('INACTIVE', 'Nonaktif'),
)

class EmployeeSalaryProfile(models.Model):
    # Relasi 1-ke-1 ke Employee (setiap Employee hanya memiliki satu profil gaji aktif)
    employee = models.OneToOneField(
        Employee, 
        on_delete=models.CASCADE, 
        related_name='salary_profile'
    )
    
    # --- KOMPONEN PENGHITUNGAN GAJI DASAR ---
    
    # Jika gaji dihitung per jam
    hourly_rate = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'), 
        verbose_name="Upah per Jam"
    )
    # Jumlah jam kerja standar (untuk hitungan gaji bulanan)
    standard_work_hours = models.PositiveIntegerField(
        default=176, 
        verbose_name="Jumlah Jam Kerja Standar (Bulan)"
    )

    # --- TUNJANGAN (ALLOWANCES) ---
    
    total_allowances = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0.00'), 
        verbose_name="Total Tunjangan Tetap"
    )
    allowance_details = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Detail Tunjangan (Tunjangan Makan, Transport, dll.)"
    )

    # --- POTONGAN (DEDUCTIONS) ---
    
    total_deductions = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0.00'), 
        verbose_name="Total Potongan Tetap"
    )
    deduction_details = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Detail Potongan (Pinjaman, Iuran)"
    )

    # --- INFORMASI LAINNYA ---
    
    effective_date = models.DateField(
        auto_now_add=True, 
        verbose_name="Tanggal Efektif Berlaku"
    )
    status = models.CharField(
        max_length=12, 
        choices=SALARY_STATUS_CHOICES, 
        default='ACTIVE', 
        verbose_name="Status Profil Gaji"
    )
    
    # --- FIELD TAMBAHAN YANG DIPERLUKAN ---
    
    # Contoh: Field untuk mencatat tunjangan PPh 21 (jika ditanggung perusahaan)
    tax_borne_by_company = models.BooleanField(
        default=False, 
        verbose_name="PPh 21 Ditanggung Perusahaan"
    )
    
    # Contoh: Field untuk mencatat keterangan atau catatan terkait gaji
    notes = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Catatan Tambahan"
    )

    class Meta:
        verbose_name = "Profil Gaji Karyawan"
        verbose_name_plural = "Profil Gaji Karyawan"

    def __str__(self):
        return f"Gaji {self.employee.name} (Per Jam: {self.hourly_rate})"

    @property
    def monthly_basic_salary(self):
        """Menghitung gaji pokok bulanan berdasarkan rate per jam dan jam kerja standar."""
        return self.hourly_rate * self.standard_work_hours


# Status Transaksi Pembayaran
TRANSACTION_STATUS_CHOICES = (
    ('SUCCESS', 'Sukses'),
    ('PENDING', 'Pending'),
    ('FAILED', 'Gagal'),
)

class PayrollHistory(models.Model):
    # --- RELASI KARYAWAN & SLIP GAJI ---
    
    # Karyawan yang menerima gaji
    employee = models.ForeignKey(
        Employee, 
        on_delete=models.PROTECT, 
        related_name='payroll_history',
        verbose_name="Karyawan"
    )
    
    # Relasi ke slip gaji yang dibayarkan (Asumsi PayrollRecord adalah slip gaji bulanan)
    payroll_record = models.ForeignKey(
        'PayrollRecord', # Menggunakan string jika PayrollRecord didefinisikan di bawah
        on_delete=models.PROTECT, 
        related_name='payment_history',
        verbose_name="Slip Gaji Bulan Ini"
    )
    
    # --- DETAIL TRANSAKSI ---
    
    transaction_date = models.DateTimeField(
        default=timezone.now, 
        verbose_name="Tanggal Transaksi Pembayaran"
    )
    
    # Data Bank Pengirim (Perusahaan)
    sender_bank_name = models.CharField(
        max_length=100, 
        verbose_name="Bank Pengirim (Perusahaan)"
    )
    sender_account_number = models.CharField(
        max_length=50, 
        verbose_name="No. Rek. Pengirim"
    )

    # Data Bank Penerima (Karyawan)
    recipient_bank_name = models.CharField(
        max_length=100, 
        verbose_name="Bank Penerima (Karyawan)"
    )
    recipient_account_number = models.CharField(
        max_length=50, 
        verbose_name="No. Rek. Penerima"
    )
    
    # --- STATUS & KETERANGAN ---
    
    status = models.CharField(
        max_length=12, 
        choices=TRANSACTION_STATUS_CHOICES, 
        default='PEND',
        verbose_name="Status Pembayaran"
    )
    
    transaction_reference = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name="Nomor Referensi Transaksi"
    )
    
    notes = models.TextField(
        blank=True, 
        null=True,
        verbose_name="Keterangan Tambahan"
    )

    class Meta:
        verbose_name = "Riwayat Pembayaran Gaji"
        verbose_name_plural = "Riwayat Pembayaran Gaji"
        # Memastikan tidak ada pembayaran ganda untuk slip gaji yang sama
        unique_together = ('payroll_record', 'status') 

    def __str__(self):
        return f"Pembayaran Gaji {self.employee.name} - {self.status}"