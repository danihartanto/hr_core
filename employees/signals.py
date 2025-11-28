from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Employee
from users.models import SystemUser
from payroll.models import EmployeeSalaryProfile # <-- Import Model baru Anda
from decimal import Decimal

# @receiver(post_save, sender=Employee)
# def create_system_user(sender, instance, created, **kwargs):
#     # Logika hanya berjalan saat objek Employee baru DIBUAT (created=True)
#     if created:
#         # Cek apakah SystemUser sudah ada untuk Employee ini
#         if hasattr(instance, 'system_user'):
#              return # User sudah ada, hentikan proses

#         # Pengecekan Ketersediaan Email
#         if not instance.email:
#              # Jika email kosong, gunakan employee_id sebagai fallback
#              username = instance.employee_id 
#         else:
#              # --- LOGIKA EKSTRAKSI USERNAME DARI EMAIL ---
#              try:
#                  # Memisahkan email menjadi username dan domain (contoh: joko@domain.com -> joko)
#                  username, domain = instance.email.split('@', 1)
#                  print("username: ",username)
#                  print("domain: ",domain)
#              except ValueError:
#                  # Jika format email salah, gunakan employee_id sebagai fallback
#                  username = instance.employee_id 

#         # Tentukan Password Awal
#         password_default = username
        
#         # 1. Pastikan username yang dihasilkan belum ada di tabel auth.User
#         if User.objects.filter(username=username).exists():
#             # Jika username sudah ada, tambahkan ID di belakangnya (atau logika lain)
#             username = f"{username}_{instance.id}" 

#         # 2. Buat objek auth.User bawaan Django
#         user = User.objects.create_user(
#             username=username,
#             is_active=True, 
#             email=instance.email or '', # Gunakan email karyawan
#         )
#         user.set_password(password_default)
#         user.save()

#         # 3. Buat objek SystemUser custom
#         SystemUser.objects.create(
#             user=user,
#             employee=instance,
#             level_user='employee', # Default: Employee Basic
#             user_status=True,
#         )

# @receiver(post_save, sender=Employee)
@receiver(post_save, sender=Employee)
def handle_employee_creation(sender, instance, created, **kwargs):
    if created:
        
        # --- 1. Logika Pembuatan User (SystemUser & auth.User) ---
        
        # Pastikan username diambil dengan aman
        username = instance.email.split('@', 1)[0] if instance.email else instance.employee_id
        
        # Cek duplikasi username (diperlukan karena ID auto-generate)
        if User.objects.filter(username=username).exists():
            username = f"{username}_{instance.id}" 

        user = User.objects.create_user(
            username=username,
            email=instance.email or '',
            is_active=True,
        )
        user.set_password(username)
        user.save()

        SystemUser.objects.create(
            user=user, 
            employee=instance, # Hanya objek instance yang diteruskan
            level_user='employee', 
            user_status=True,
        )

        # --- 2. Logika Pembuatan Profil Gaji Default ---
        EmployeeSalaryProfile.objects.create(
            employee=instance, # Hanya objek instance yang diteruskan
            hourly_rate=Decimal('20000.00'), 
            total_allowances=Decimal('0.00'),
            total_deductions=Decimal('0.00'),
            status='ACTIVE'
        )