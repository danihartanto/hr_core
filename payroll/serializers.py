# payroll/serializers.py

from rest_framework import serializers
from .models import Overtime, PayrollRecord
from employees.models import Employee

# --- Overtime Serializer ---
class OvertimeSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    
    class Meta:
        model = Overtime
        fields = '__all__'
        
# --- Payroll Record Serializer ---
# class PayrollRecordSerializer(serializers.ModelSerializer):
#     employee_name = serializers.CharField(source='employee.name', read_only=True)
#     # Menampilkan teks status pembayaran (misal: "Settled")
#     payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)

#     class Meta:
#         model = PayrollRecord
#         fields = '__all__'
class PayrollRecordSerializer(serializers.ModelSerializer):
    # Mengubah employee menjadi PrimaryKeyRelatedField untuk input (write)
    # yang menerima ID Karyawan.
    employee = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all()
    )
    
    # Field display (read-only) tetap ada untuk output API
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)
    salary_type_display = serializers.CharField(source='get_salary_type_display', read_only=True)

    class Meta:
        model = PayrollRecord
        fields = '__all__'

    # --- Implementasi Logika Pengambilan Gaji Otomatis ---
    def validate(self, data):
        """
        Mengambil salary dari objek Employee yang dipilih dan
        mengisinya ke basic_salary sebelum disimpan.
        """
        # 1. Ambil objek Employee dari data yang divalidasi
        employee = data.get('employee')
        
        # 2. Ambil nilai salary dari objek Employee
        employee_salary = employee.salary
        
        # 3. Masukkan nilai salary ke basic_salary jika belum diisi manual
        # Jika basic_salary sudah diisi di request, biarkan (opsional: bisa dipaksa ambil dari employee)
        if 'basic_salary' not in data:
            data['basic_salary'] = employee_salary
        
        # Jika salary_type yang dibuat adalah 'GAJI' dan basic_salary belum diisi, ambil dari employee
        # if data.get('salary_type') == 'GAJI' and 'basic_salary' not in data:
        #    data['basic_salary'] = employee_salary
        
        return data