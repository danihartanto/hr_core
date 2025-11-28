"""
URL configuration for hr_core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.conf import settings
from django.conf.urls.static import static
from users.views import CustomTokenObtainPairView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Endpoint untuk mendapatkan Access Token dan Refresh Token (Login)
    # path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # Endpoint untuk memperbarui Access Token (setelah kadaluarsa)
    # path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Ganti TokenObtainPairView standar dengan CustomTokenObtainPairView
    path('api/v1/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    path('api/v1/', include('users.urls')),

    # URL untuk aplikasi karyawan (CRUD)
    path('api/v1/employees/', include('employees.urls')),
    # URL Struktur Organisasi (CRUD)
    path('api/v1/organization/', include('organization.urls')),
    # URL Aplikasi Payroll (Penggajian & Lembur)
    path('api/v1/payroll/', include('payroll.urls')),
    # URL Aplikasi Attendance (Absensi, Cuti, & Hari Libur)
    path('api/v1/attendance/', include('attendance.urls')),
]

# --- Tambahkan konfigurasi static files di DEVELOPMENT (DEBUG=True) ---
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)