from django.urls import path, include
from rest_framework.routers import DefaultRouter # type: ignore
from .views import UserProfileViewSet, UserListViewSet

router = DefaultRouter()
# Daftarkan UserProfileViewSet (perhatikan base_name: 'users')
# router.register(r'users', UserProfileViewSet, basename='users') 
# 1. Endpoint untuk Profil User Aktif (/users/me/ & /users/reset_password/)
router.register(r'users', UserProfileViewSet, basename='users') 

# 2. Endpoint BARU untuk Daftar Semua User (GET /users-list/)
# Kita menggunakan path yang berbeda agar tidak bentrok dengan /users/me/
router.register(r'users-list', UserListViewSet, basename='users-list')


urlpatterns = [
    path('', include(router.urls)),
]