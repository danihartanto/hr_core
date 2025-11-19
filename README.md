# hr_core aplikasi management Human Resource

# 🚀 Tutorial Awal REST API HR (Django + MySQL + JWT)
## 1️⃣ **Tahap 1: Persiapan Lingkungan**
*Pastikan Anda sudah menginstal Python 3.10+.*
1. Buat dan Aktifkan Virtual Environment.  
    Penggunaan virtual environment sangat penting untuk mengisolasi dependensi proyek Anda.
    ```
    #Membuat environment 
    python3 -m venv hr_api_env
    
    # Mengaktifkan environment (Linux/macOS)
    source hr_api_env/bin/activate

    # Mengaktifkan environment (Windows - PowerShell)
    .\hr_api_env\Scripts\activate
    
    ```
2. Instalasi Dependensi Inti  
Kita akan menginstal Django, Django REST Framework, dan paket yang dibutuhkan untuk JWT dan MySQL.
    ```
    pip install django djangorestframework djangorestframework-simplejwt mysqlclient
    ```
    * django: Kerangka kerja utama.
    * djangorestframework: Untuk membuat REST API.
    * djangorestframework-simplejwt: Untuk otentikasi JWT.
    * mysqlclient: Adaptor Python untuk menghubungkan ke MySQL.

## 2️⃣ **Tahap 2: Setup Proyek Django**
1. Buat Proyek dan Aplikasi  
    ```
    # Buat proyek Django
    django-admin startproject hr_core .

    # Buat aplikasi (misalnya 'employees' dan 'users' untuk otentikasi)
    python manage.py startapp employees
    python manage.py startapp users
    ```
2. Konfigurasi MySQL (hr_core/settings.py)  
Ubah pengaturan database Anda. Pastikan Anda sudah membuat database kosong bernama hr_db di server MySQL Anda.
    ```
    # hr_core/settings.py

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'hr_db', # Nama database yang Anda buat
            'USER': 'your_mysql_user', # Ganti dengan username MySQL Anda
            'PASSWORD': 'your_mysql_password', # Ganti dengan password MySQL Anda
            'HOST': '127.0.0.1',
            'PORT': '3306',
        }
    }
    ```
3. Konfigurasi Aplikasi dan REST Framework (hr_core/settings.py)  
Tambahkan aplikasi baru dan framework yang diinstal ke INSTALLED_APPS.
    ```
    # hr_core/settings.py

    INSTALLED_APPS = [
        # ... aplikasi bawaan
        'django.contrib.staticfiles',

        # Aplikasi pihak ketiga
        'rest_framework',
        'rest_framework_simplejwt',

        # Aplikasi lokal
        'users.apps.UsersConfig',
        'employees.apps.EmployeesConfig',
    ]
    ```
4. Jalankan Migrasi Awal  
Migrasi ini akan membuat tabel sistem Django dan JWT di database MySQL Anda.
    ```
    # run satu persatu pada terminal
    python manage.py makemigrations
    python manage.py migrate
    ```

## 3️⃣ **Tahap 3: Implementasi Otentikasi JWT**
Kita akan menggunakan Simple JWT untuk menangani login dan refresh token.
1. Konfigurasi Simple JWT (hr_core/settings.py)  
Tambahkan konfigurasi default untuk Simple JWT.
    ```
    # hr_core/settings.py
    # Konfigurasi REST Framework
    REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': (
            # Gunakan JWT sebagai metode autentikasi default
            'rest_framework_simplejwt.authentication.JWTAuthentication',
        ),
        'DEFAULT_PERMISSION_CLASSES': (
            # Secara default, semua endpoint memerlukan autentikasi
            'rest_framework.permissions.IsAuthenticated',
        )
    }

    # Konfigurasi Simple JWT (Opsional, tetapi disarankan)
    from datetime import timedelta

    SIMPLE_JWT = {
        'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60), # Masa berlaku token akses
        'REFRESH_TOKEN_LIFETIME': timedelta(days=1),   # Masa berlaku token refresh
        'ROTATE_REFRESH_TOKENS': True,
        'BLACKLIST_AFTER_ROTATION': True,
        'ALGORITHM': 'HS256',
        'SIGNING_KEY': SECRET_KEY, # Menggunakan SECRET_KEY Django
        # ... konfigurasi lainnya
    }
    ```
2. Konfigurasi URL Otentikasi (hr_core/urls.py)  
Tambahkan endpoint yang disediakan oleh Simple JWT untuk mendapatkan token (/api/token/) dan me-refresh token (/api/token/refresh/).
    ```
    # hr_core/urls.py
    from django.contrib import admin
    from django.urls import path, include
    from rest_framework_simplejwt.views import (
        TokenObtainPairView,
        TokenRefreshView,
    )

    urlpatterns = [
        path('admin/', admin.site.urls),
        
        # Endpoint untuk mendapatkan Access Token dan Refresh Token (Login)
        path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
        
        # Endpoint untuk memperbarui Access Token (setelah kadaluarsa)
        path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

        # URL untuk aplikasi karyawan
        path('api/v1/employees/', include('employees.urls')),
    ]
    ```

## 4️⃣ **Tahap 4: Membuat Endpoint Karyawan (Employees)**
1. Buat Model Karyawan (employees/models.py)  
Definisikan struktur data untuk entitas Karyawan.
    ```
    # employees/models.py

    from django.db import models

    class Employee(models.Model):
        name = models.CharField(max_length=100)
        employee_id = models.CharField(max_length=20, unique=True)
        position = models.CharField(max_length=50)
        department = models.CharField(max_length=50)
        hire_date = models.DateField()
        salary = models.DecimalField(max_digits=10, decimal_places=2)

        def __str__(self):
            return self.name
    ```
2. Buat Serializer (employees/serializers.py)  
Serializer mengubah data Model menjadi JSON dan sebaliknya.
    ```
    # employees/serializers.py
    from rest_framework import serializers
    from .models import Employee

    class EmployeeSerializer(serializers.ModelSerializer):
        class Meta:
            model = Employee
            fields = '__all__'
    ```
3. Buat ViewSet (employees/views.py)  
ViewSet menyediakan operasi CRUD (Create, Retrieve, Update, Delete) secara otomatis.
    ```
    # employees/views.py
    from rest_framework import viewsets
    from .models import Employee
    from .serializers import EmployeeSerializer
    from rest_framework.permissions import IsAuthenticated

    class EmployeeViewSet(viewsets.ModelViewSet):
        queryset = Employee.objects.all().order_by('name')
        serializer_class = EmployeeSerializer
        # Hanya pengguna yang telah terautentikasi yang boleh mengakses endpoint ini
        permission_classes = [IsAuthenticated]
    ```
4. Konfigurasi URL Aplikasi (employees/urls.py)  
Gunakan Router DRF untuk menghasilkan semua rute secara otomatis.
    ```
    # employees/urls.py
    from django.urls import path, include
    from rest_framework.routers import DefaultRouter
    from .views import EmployeeViewSet

    router = DefaultRouter()
    # Mendaftarkan EmployeeViewSet ke /employees/
    router.register(r'', EmployeeViewSet) 

    urlpatterns = [
        path('', include(router.urls)),
    ]
    ```

## 5️⃣ **Tahap 5: Uji Coba**
1. Buat Superuser  
Anda membutuhkan pengguna untuk login dan mendapatkan token.
    ```
    #run berikut pada terminal
    python manage.py createsuperuser
    ```
    Ikuti petunjuk untuk membuat username dan password.  
2. Jalankan Server  
    ```
    python manage.py runserver
    ```
3. Uji Coba API (Menggunakan Postman/Insomnia/cURL)  
    * A. Login dan Dapatkan Token
        - URL: http://127.0.0.1:8000/api/token/
        - Method: POST
        - Body (JSON):
            ```
            {
                "username": "your_superuser_name",
                "password": "your_password"
            }
            ```
        - Respons: Anda akan menerima access token dan refresh token.
            ```
            {
                "refresh": "...",
                "access": "..." 
            }
            ```
    * B. Akses Endpoint Karyawan (Membutuhkan Otentikasi)
        - URL: http://127.0.0.1:8000/api/v1/employees/
        - Method: GET
        - Header:
            - Key: Authorization
            - Value: Bearer <TEMP_ACCESS_TOKEN_DARI_LANGKAH_A>  
            
        Jika berhasil, Anda akan mendapatkan respons 200 OK (daftar karyawan kosong/belum ada). Jika Anda tidak menyertakan header Authorization, Anda akan mendapatkan 401 Unauthorized.