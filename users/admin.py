from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from users.models import SystemUser # Pastikan ini sudah di-import

# 1. Definisikan Inline untuk SystemUser
class SystemUserInline(admin.StackedInline):
    model = SystemUser
    can_delete = False  # Biasanya tidak diizinkan menghapus SystemUser saat mengedit User
    verbose_name_plural = 'Informasi Sistem Pengguna'
    
    # Tampilkan field level_user (employee, staff, manager, admin)
    fields = (
        'level_user', 
        'user_status' # Tambahkan user_status juga jika perlu diatur
    )

# 2. Definisikan Admin Kustom untuk Model User
# Kita akan menimpa (override) UserAdmin bawaan Django
class UserAdmin(BaseUserAdmin):
    # Daftarkan inline yang baru dibuat
    inlines = (SystemUserInline,)
    
    # Tambahkan field system user ke fieldset utama (Opsional)
    # Jika Anda ingin menampilkan field SystemUser di salah satu fieldset
    # Catatan: Kita sudah menampilkannya melalui Inline, jadi ini opsional.
    
    # Kita tidak perlu mengubah fieldsets bawaan User, kecuali jika Anda ingin menambahkan field Employee
    # ...
    pass


# 3. Batalkan Pendaftaran User dan Daftarkan yang Baru
# Ini penting untuk mengganti UserAdmin bawaan Django dengan UserAdmin kustom kita.
admin.site.unregister(User)
admin.site.register(User, UserAdmin)