# hr_core aplikasi management Human Resource

# 🚀 Tutorial Awal REST API HR (Django + MySQL + JWT)
## **Tahap 1: Persiapan Lingkungan**
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

## **Tahap 2: Setup Proyek Django**
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