from rest_framework import serializers # Import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from decimal import Decimal
from users.models import SystemUser
from employees.models import Employee
from payroll.models import EmployeeSalaryProfile
from django.contrib.auth.models import User

class TokenSalaryProfileSerializer(serializers.ModelSerializer):
    monthly_basic_salary = serializers.SerializerMethodField()

    class Meta:
        model = EmployeeSalaryProfile
        # Pilih field yang ingin Anda tampilkan di respons token
        fields = (
            'hourly_rate', 
            'standard_work_hours', 
            'total_allowances', 
            'total_deductions',
            'monthly_basic_salary',
        )

    def get_monthly_basic_salary(self, obj):
        # Mengambil property dari model dan mengkonversi Decimal ke string
        try:
            return str(obj.monthly_basic_salary)
        except Exception:
            return "0.00"
        
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer kustom yang menimpa metode validate() untuk menambahkan
    data pengguna dan level ke response token.
    """
    def validate(self, attrs):
        # 1. Memanggil metode validate() asli untuk mendapatkan token
        data = super().validate(attrs)

        # 2. Ambil objek User yang terotentikasi
        user = self.user 
        
        # Inisialisasi data user default
        user_data = {
            'id': user.id,
            'user_employee_id': None,
            'employee_id': None,
            'full_name': user.username, # Default menggunakan username
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'username': user.username,
            'level_user': 'Undefined',
            'level_user_code': None,
            'user_status': user.is_active,
        }

        # 3. Ambil data dari SystemUser dan Employee
        try:
            # Cek relasi OneToOne
            system_user = SystemUser.objects.get(user=user)
            employee = system_user.employee
            
            # Ambil profil gaji (melalui related_name='salary_profile')
            salary_profile = employee.salary_profile 
            
            # --- PENAMBAHAN: Serialisasi Detail Gaji ---
            salary_data = TokenSalaryProfileSerializer(salary_profile).data
            
            # Timpa data user dengan informasi lengkap
            user_data['level_user'] = system_user.get_level_user_display() # Menggunakan display name (misal: 'HR Staff')
            user_data['level_user_code'] = system_user.level_user # Kode level (misal: 'HR')
            user_data['user_status'] = system_user.user_status
            user_data['employee_id'] = employee.employee_id
            user_data['full_name'] = employee.name
            user_data['telepon'] = employee.telepon
            user_data['user_employee_id'] = employee.id
            # --- MASUKKAN DETAIL GAJI KE USER DATA ---
            user_data['salary_profile'] = salary_data
            
        # except (SystemUser.DoesNotExist, Employee.DoesNotExist):
        #     # Jika user adalah Superuser atau user tanpa relasi Employee/SystemUser
        #     if user.is_superuser:
        #          user_data['level_user'] = 'System Administrator'

        # # 4. Tambahkan data user ke response body
        # data['user'] = user_data

        # return data
        except (SystemUser.DoesNotExist, EmployeeSalaryProfile.DoesNotExist, Employee.DoesNotExist):
            # Handle jika profil gaji/user tidak lengkap
            user_data['level_user'] = 'Administrator System' if user.is_superuser else 'Unassigned'
            user_data['salary_profile'] = None # Data gaji kosong jika tidak ditemukan

        # Tambahkan data user ke response body
        data['user'] = user_data

        return data

# --- 1. Serializer untuk Update Profil User ---
class UserProfileUpdateSerializer(serializers.ModelSerializer):
    # Field dari SystemUser
    level_user = serializers.CharField(required=False)
    user_status = serializers.BooleanField(required=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'level_user', 'user_status')
        read_only_fields = ('username',) # Username tidak boleh diubah

    def update(self, instance, validated_data):
        # Ambil data dari SystemUser jika ada
        system_user_data = {
            'level_user': validated_data.pop('level_user', None),
            'user_status': validated_data.pop('user_status', None)
        }
        
        # 1. Update fields di Model auth.User
        instance = super().update(instance, validated_data)

        # 2. Update fields di Model SystemUser
        try:
            system_user = instance.systemuser # Mengakses related_name dari OneToOneField
            if system_user_data['level_user'] is not None:
                system_user.level_user = system_user_data['level_user']
            if system_user_data['user_status'] is not None:
                system_user.user_status = system_user_data['user_status']
            system_user.save()
        except SystemUser.DoesNotExist:
            # Lewati jika user adalah superuser tanpa SystemUser
            pass

        return instance

# --- 2. Serializer untuk Reset Password ---
class PasswordResetSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)