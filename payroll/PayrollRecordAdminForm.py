from django.contrib import admin
from django import forms
from .models import Overtime, PayrollRecord
# Import model Employee untuk mengambil data salary
from employees.models import Employee 

# --- 1. Custom Form untuk Admin PayrollRecord ---
class PayrollRecordAdminForm(forms.ModelForm):
    class Meta:
        model = PayrollRecord
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # PENTING: Menambahkan atribut data-employee-salary ke dropdown Employee
        # Ini memungkinkan JavaScript di Langkah 2 untuk membaca gaji
        employee_queryset = self.fields['employee'].queryset
        employee_data = {
            employee.id: employee.salary for employee in employee_queryset
        }
        # Menyimpan data gaji sebagai atribut data di field employee
        self.fields['employee'].widget.attrs['data-employee-salaries'] = employee_data
        
        # Jika instance sudah ada (mode edit), set basic_salary jika belum ada
        if self.instance and not self.instance.pk and self.instance.employee_id:
            try:
                # Mengambil gaji saat form dimuat untuk instance baru
                employee_instance = Employee.objects.get(id=self.instance.employee_id)
                self.initial['basic_salary'] = employee_instance.salary
            except Employee.DoesNotExist:
                pass


# --- 2. Daftarkan Model Admin dengan Custom Form ---

@admin.register(PayrollRecord)
class PayrollRecordAdmin(admin.ModelAdmin):
    form = PayrollRecordAdminForm # <-- Gunakan custom form di sini
    
    list_display = (
        'employee', 'pay_year', 'pay_month', 
        'salary_type', 
        'net_salary', 'payment_status'
    )
    list_filter = ('pay_year', 'pay_month', 'payment_type', 'salary_type')
    search_fields = ('employee__name', 'employee__employee_id')
    
    fieldsets = (
        ('Periode & Karyawan', {
            'fields': ('employee', ('pay_year', 'pay_month'), 'salary_type', 'payment_status') 
        }),
        ('Penghasilan Bruto', {
            # Pastikan basic_salary ada di field ini
            'fields': ('basic_salary', 'allowances', 'overtime_pay', 'gross_salary')
        }),
        ('Potongan & Neto', {
            'fields': ('tax_deduction', 'bpjs_deduction', 'other_deductions', 'net_salary')
        }),
    )
    # Field hasil perhitungan
    readonly_fields = ('gross_salary', 'net_salary',) 
    
# ... (OvertimeAdmin tetap sama) ...