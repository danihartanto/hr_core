# organization/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CompanyViewSet, 
    GroupHeadViewSet, 
    DepartmentViewSet, 
    UnitViewSet, 
    JobTitleViewSet
)

# Inisialisasi Router
router = DefaultRouter()

# Mendaftarkan ViewSets ke Router
router.register(r'companies', CompanyViewSet)
router.register(r'group-heads', GroupHeadViewSet)
router.register(r'departments', DepartmentViewSet)
router.register(r'units', UnitViewSet)
router.register(r'job-titles', JobTitleViewSet)

# Pola URL aplikasi organization
urlpatterns = [
    # Semua URL CRUD dari router akan di-include di sini
    path('', include(router.urls)),
]