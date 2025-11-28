from django.contrib import admin
from .models import Employee
from payroll.models import EmployeeSalaryProfile


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    # Kolom yang ditampilkan di daftar utama
    list_display = ('employee_id', 'name', 'email','telepon', 'job_title', 'gender','born_place', 'born_date', 'religion', 'hire_date','terminate_date')
    
    # Filter samping
    list_filter = ('job_title', 'hire_date')
    
    # Kolom yang bisa dicari
    search_fields = ('name', 'employee_id')
    
    # Kolom yang bisa langsung diedit dari daftar utama
    # list_editable = ('salary',) 

    # Fieldset untuk tata letak form edit
    fieldsets = (
        ('Personal Info', {
            'fields': ('name', 'employee_id', 'email', 'telepon', 'gender', 'born_place', 'born_date', 'religion', 'hire_date','terminate_date')
        }),
        ('Organizational Role', {
            # job_title terhubung ke hierarki organization
            'fields': ('job_title',) 
        }),
        
        # ('Compensation', {
        #     'fields': ('salary',)
        # }),
    )
    readonly_fields = ('employee_id',)

class EmployeeSalaryProfileInline(admin.StackedInline):
    model = EmployeeSalaryProfile
    can_delete = False  # Biasanya tidak boleh dihapus langsung
    verbose_name_plural = 'Profil Gaji Aktif'
    # Field yang ingin ditampilkan
    fields = (
        'status', 'hourly_rate', 'standard_work_hours', 
        'total_allowances', 'allowance_details',
        'total_deductions', 'deduction_details',
        'tax_borne_by_company', 'notes', 'effective_date'
    )
    readonly_fields = ('effective_date',) # Tanggal efektif diisi otomatis
