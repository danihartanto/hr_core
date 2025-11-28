from django.contrib import admin
from .models import Attendance, LeaveRequest, NationalHoliday

# --- Absensi Harian ---
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = (
        'employee', 'date', 'check_in', 
        'check_out', 'is_late',
        'total_hours'
    )
    list_filter = ('date', 'is_late')
    search_fields = ('employee__name', 'employee__employee_id')
    
# --- Permintaan Cuti ---
@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = (
        'employee', 'leave_type', 'start_date', 
        'end_date', 'days_requested', 'status', 
        'approved_by'
    )
    # Filter utama yang paling penting
    list_filter = ('status', 'leave_type', 'start_date')
    search_fields = ('employee__name', 'reason')
    
    # Form edit dibagi menjadi beberapa bagian
    fieldsets = (
        ('Info Permintaan', {
            'fields': ('employee', 'leave_type', 'days_requested', 'reason')
        }),
        ('Periode Cuti', {
            'fields': ('start_date', 'end_date')
        }),
        ('Persetujuan (HR/Manajer)', {
            'fields': ('status', 'approved_by')
        })
    )
    
# --- Hari Libur Nasional ---
@admin.register(NationalHoliday)
class NationalHolidayAdmin(admin.ModelAdmin):
    list_display = ('date', 'name', 'is_national')
    list_filter = ('is_national',)
    search_fields = ('name',)
    list_editable = ('is_national',) # Bisa diubah langsung dari daftar