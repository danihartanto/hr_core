# # employees/serializers.py

# from rest_framework import serializers
# from .models import Employee

# class EmployeeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Employee
#         fields = '__all__'
# employees/serializers.py

from rest_framework import serializers
from .models import Employee
# PENTING: Import semua Model dari aplikasi 'organization'
from organization.models import JobTitle, Unit, Department, GroupHead, Company 
from payroll.models import EmployeeSalaryProfile 
from decimal import Decimal

# --- SERIALIZER HIRARKI ORGANISASI (Hanya untuk Display) ---

# 1. Company
class NestedCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ('id', 'name')
        
# 2. Group Head (dengan nested Company)
class NestedGroupHeadSerializer(serializers.ModelSerializer):
    company = NestedCompanySerializer(read_only=True) # <-- Nested
    class Meta:
        model = GroupHead
        fields = ('id', 'name', 'company')
        
# 3. Department (dengan nested GroupHead)
class NestedDepartmentSerializer(serializers.ModelSerializer):
    group_head = NestedGroupHeadSerializer(read_only=True) # <-- Nested
    class Meta:
        model = Department
        fields = ('id', 'name', 'group_head')

# 4. Unit (dengan nested Department)
class NestedUnitSerializer(serializers.ModelSerializer):
    department = NestedDepartmentSerializer(read_only=True) # <-- Nested
    class Meta:
        model = Unit
        fields = ('id', 'name', 'department')
        
# 5. Job Title (dengan nested Unit, dan Level Display)
class NestedJobTitleSerializer(serializers.ModelSerializer):
    # Menampilkan teks Band (misal: "Level 1 (Band 1) - Direktur")
    level_display = serializers.CharField(source='get_level_display', read_only=True) 
    
    # Unit membawa Department -> GroupHead -> Company
    unit = NestedUnitSerializer(read_only=True) # <-- Nested
    
    class Meta:
        model = JobTitle
        # Menampilkan unit sebagai objek, bukan hanya ID
        fields = ('id', 'title_name', 'level', 'level_display', 'unit')
        
# --- SERIALIZER KARYAWAN UTAMA ---

class EmployeeSerializer(serializers.ModelSerializer):
    # Mengganti field job_title default dengan Nested Serializer yang baru
    # read_only=True memastikan ini hanya untuk tampilan (display)
    job_title = NestedJobTitleSerializer(read_only=True) 
    job_title_display = NestedJobTitleSerializer(source='job_title', read_only=True)
    job_title = serializers.PrimaryKeyRelatedField(
        queryset=JobTitle.objects.all(),
        write_only=True # Agar field ini hanya muncul di form input, bukan di output JSON utama
    )
    # all_employee_salaries = serializers.SerializerMethodField()
    class Meta:
        model = Employee
        # fields = '__all__'
        fields = (
            'id', 'name', 'employee_id', 
            'email',
            'telepon',
            'born_place',
            'born_date',
            'gender',
            'religion',
            'job_title_display',
            'job_title', 
            'hire_date', 
            'terminate_date',
            # 'salary',
            # 'all_employee_salaries' # <-- Tambahkan field baru di output
        )
        # Catatan: Jika Anda ingin client bisa mengupdate job_title, 
        # Anda harus menambahkan field PrimaryKeyRelatedField terpisah 
        # untuk operasi POST/PUT/PATCH.
    # def get_all_employee_salaries(self, obj):
    #     """
    #     Mengambil ID dan Salary dari SEMUA karyawan untuk digunakan pada dropdown client.
    #     Field ini hanya akan muncul saat mengambil list karyawan (objek self.many adalah True).
    #     """
    #     # Kita hanya ingin data ini muncul sekali (misalnya, saat list pertama diambil)
    #     # Jika Anda memanggil get_all_employee_salaries di EmployeeSerializer saat instance tunggal, 
    #     # maka dia akan mengembalikan data yang sama berulang-ulang.
        
    #     # Untuk kasus ini, kita akan kembalikan data per instance, tetapi di client 
    #     # kita hanya perlu mengambilnya sekali dari salah satu objek.
        
    #     # Ambil data semua karyawan (hanya ID dan Salary)
    #     salaries = Employee.objects.all().values('id', 'salary')
        
    #     # Konversi ke dictionary agar mudah diakses di JavaScript: {id: salary}
    #     salary_map = {
    #         str(s['id']): str(s['salary']) 
    #         for s in salaries
    #     }
    #     return salary_map

class EmployeeSalaryProfileSerializer(serializers.ModelSerializer):
    # Menggunakan SerializerMethodField untuk monthly_basic_salary
    monthly_basic_salary = serializers.SerializerMethodField()

    class Meta:
        model = EmployeeSalaryProfile
        # Tampilkan semua field yang relevan untuk gaji
        fields = (
            'hourly_rate', 'standard_work_hours', 
            'monthly_basic_salary', 
            'total_allowances', 'allowance_details',
            'total_deductions', 'deduction_details', 
            'status', 'effective_date'
        )

    def get_monthly_basic_salary(self, obj):
        # Memanggil property dari model
        # Kita perlu mengkonversi Decimal ke string agar aman di JSON
        return str(obj.monthly_basic_salary)


# --- SERIALIZER GABUNGAN UNTUK ENDPOINT /salary ---
class EmployeeSalaryDetailSerializer(serializers.ModelSerializer):
    # Relasi ke Jabatan (Nested)
    job_title = NestedJobTitleSerializer(read_only=True)
    
    # Relasi ke Profil Gaji (Nested)
    # Gunakan related_name='salary_profile' dari OneToOneField di Model
    salary_profile = EmployeeSalaryProfileSerializer(read_only=True)

    class Meta:
        model = Employee
        fields = (
            'id', 'employee_id', 'name', 'email', 
            'job_title', 
            'salary_profile' # <-- Ini akan menampilkan detail gaji
        )