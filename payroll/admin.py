from django.contrib import admin
from .models import Overtime, PayrollRecord, EmployeeSalaryProfile, PayrollHistory
from django import forms
# Import model Employee untuk mengambil data salary
from employees.models import Employee
import json # Import json untuk serialisasi
from decimal import Decimal

# Fungsi pembantu untuk mengkonversi Decimal ke String (JSON serializable)
def decimal_default(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")
@admin.register(Overtime)
class OvertimeAdmin(admin.ModelAdmin):
    # Kolom yang ditampilkan di daftar utama
    list_display = (
        'employee', 'date', 'duration_hours', 
        'rate_multiplier', 'is_approved'
    )
    # Filter samping
    list_filter = ('is_approved', 'date')
    # Kolom yang bisa dicari
    search_fields = ('employee__name', 'date')
    # Kolom yang bisa langsung diedit dari daftar utama
    list_editable = ('is_approved',)
    # Field yang ditampilkan di form edit
    fields = (
        'employee', 'date', 
        ('start_time', 'end_time'), 
        'duration_hours', 'rate_multiplier', 
        'is_approved'
    )
    
# @admin.register(PayrollRecord)
class PayrollRecordAdminForm(forms.ModelForm):
    # Field yang ingin ditampilkan di form
    
    # NOTE: Kita tidak perlu lagi memuat data gaji melalui JS
    # karena logika penarikan data sudah ada di model save()
    # Namun, kita tambahkan field untuk menampilkan basic salary terkunci
    
    class Meta:
        model = PayrollRecord
        fields = '__all__'

    # Form ini tidak lagi melakukan injeksi data ke HTML
    # karena logika penarikan data sudah dilakukan di model
    # Kecuali jika Anda ingin menampilkan gaji pokok sebagai READONLY field
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 1. Hapus logika injeksi JS (Jika ada)
        # 2. Tampilkan gaji pokok sebagai readonly (opsional)
        if 'employee' in self.fields:
            # Contoh: Membuat field employee sebagai form field biasa
            self.fields['employee'].widget.attrs = {}
            
            # Jika ini adalah form edit (objek sudah ada), tampilkan nilai yang terkunci
            if self.instance.pk:
                self.fields['locked_basic_salary'].disabled = True
                self.fields['locked_allowances'].disabled = True
                self.fields['locked_deductions'].disabled = True

# --- 2. Daftarkan Model Admin dengan Custom Form ---

@admin.register(PayrollRecord) # <-- Dekorator harus ada di sini
class PayrollRecordAdmin(admin.ModelAdmin):
    # Menggunakan custom form yang dibuat di atas
    form = PayrollRecordAdminForm 
    
    list_display = (
        'employee', 'pay_year', 'pay_month', 
        'salary_type', 
        'net_salary', 
        'payment_status'
    )
    fieldsets = (
        ('Periode & Karyawan', {
            'fields': ('employee', 'pay_year', 'pay_month', 'salary_type', 'payment_status')
        }),
        ('Pemasukan', {
            # Gunakan field yang terkunci dan field input variabel
            'fields': ('locked_basic_salary', 'locked_allowances', 'overtime_pay', 'gross_salary')
        }),
        ('Potongan', {
            # Gunakan field yang terkunci dan field input variabel
            'fields': ('tax_deduction', 'bpjs_deduction', 'locked_deductions', 'other_deductions', 'net_salary')
        }),
    )
    
    readonly_fields = (
        'gross_salary', 'net_salary', 'created_at', 'updated_at', 
        # Field yang dikunci dari profil gaji harus readonly
        'locked_basic_salary', 'locked_allowances', 'locked_deductions',
        'salary_profile_used' # Profil yang digunakan juga readonly
    )
    # ... (list_filter, search_fields, fieldsets, dll. tetap sama) ...
    
    # class Media:
    #     # Path harus dimulai dari nama aplikasi/nama file
    #     js = (
    #         'payroll/payroll_admin.js', # <-- Ini merujuk ke static/payroll/payroll_admin.js
    #     )
        # Tambahkan template custom untuk menyuntikkan JS
    # change_form_template = "admin/payroll/payrollrecord/change_form.html"
    # 3. Metode untuk memuat JavaScript di tempat yang aman (mengatasi TypeError)
# class Media:
#     js = (
#         'payroll/payroll_admin.js',
#     )

@admin.register(EmployeeSalaryProfile)
class EmployeeSalaryProfileAdmin(admin.ModelAdmin):
    # Kolom yang ditampilkan
    def employee_id_display(self, obj):
        """Menampilkan employee_id dari objek Employee yang terkait."""
        return obj.employee.employee_id
    employee_id_display.short_description = 'ID Karyawan' # Header kolom di Admin
    employee_id_display.admin_order_field = 'employee__employee_id' # Mengizinkan sorting
    
    def employee_name_display(self, obj):
        """Menampilkan nama karyawan dari objek Employee yang terkait."""
        return obj.employee.name
    employee_name_display.short_description = 'Nama Karyawan' # Header kolom di Admin
    employee_name_display.admin_order_field = 'employee__name' # Mengizinkan sorting

    # --- Gunakan custom methods di list_display ---
    list_display = (
        'employee_id_display',      # <-- ID Karyawan
        'employee_name_display',    # <-- Nama Karyawan
        'status', 
        'monthly_basic_salary', 
        'hourly_rate', 
        'total_allowances', 
        'total_deductions', 
        'effective_date'
    )
    
    list_filter = ('status', 'tax_borne_by_company')
    # Perbarui search_fields untuk memungkinkan pencarian berdasarkan ID dan Nama
    search_fields = ('employee__name', 'employee__employee_id', 'allowance_details')
    
    # ... (Fieldset dan konfigurasi lainnya tetap sama) ...
    
    readonly_fields = ('effective_date', 'monthly_basic_salary')


@admin.register(PayrollHistory)
class PayrollHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'employee', 'payroll_record', 'transaction_date', 
        'status', 'transaction_reference'
    )
    list_filter = ('status', 'transaction_date')
    search_fields = (
        'employee__name', 'employee__employee_id', 
        'transaction_reference', 'recipient_account_number'
    )
    readonly_fields = ('transaction_date',)
    
    fieldsets = (
        (None, {
            'fields': ('employee', 'payroll_record', 'status', 'transaction_date')
        }),
        ('Informasi Bank Pengirim', {
            'fields': ('sender_bank_name', 'sender_account_number')
        }),
        ('Informasi Bank Penerima', {
            'fields': ('recipient_bank_name', 'recipient_account_number')
        }),
        ('Detail Transaksi', {
            'fields': ('transaction_reference', 'notes')
        })
    )