# employees/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmployeeViewSet, EmployeeSalaryDetailView # Import View baru

# router = DefaultRouter()
# # Mendaftarkan EmployeeViewSet ke /employees/
# router.register(r'', EmployeeViewSet) 

# Jika Anda menggunakan ViewSet:
router = DefaultRouter()
router.register(r'', EmployeeViewSet) # Anda mungkin sudah memiliki ini

urlpatterns = [
    # Path untuk list/retrieve/create/update/delete (Viewset)
    path('', include(router.urls)),
    
    # --- PATH BARU YANG DIMINTA ---
    # employees/<id>/salary/
    path('<int:pk>/salary/', 
         EmployeeSalaryDetailView.as_view(), 
         name='employee-salary-detail'),
]