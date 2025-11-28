from django.shortcuts import render
# employees/views.py

from rest_framework import viewsets
from .models import Employee
from rest_framework.generics import RetrieveAPIView
from .serializers import EmployeeSerializer
from .serializers import EmployeeSalaryDetailSerializer # Import Serializer baru Anda
from rest_framework.permissions import IsAuthenticated

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all().order_by('name')
    serializer_class = EmployeeSerializer
    # Hanya pengguna yang telah terautentikasi yang boleh mengakses endpoint ini
    permission_classes = [IsAuthenticated]
    
class EmployeeSalaryDetailView(RetrieveAPIView):
    """
    Mengambil detail karyawan, jabatan, dan profil gaji berdasarkan ID karyawan.
    URL: api/v1/employees/<id>/salary/
    """
    queryset = Employee.objects.all()
    serializer_class = EmployeeSalaryDetailSerializer
    permission_classes = [IsAuthenticated] # Hanya user yang terautentikasi yang bisa akses
    # lookup_field defaultnya adalah 'pk' (ID), yang sesuai untuk /employees/1/salary
