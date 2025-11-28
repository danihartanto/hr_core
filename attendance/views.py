from django.shortcuts import render
# attendance/views.py

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Attendance, LeaveRequest, NationalHoliday
from .serializers import AttendanceSerializer, LeaveRequestSerializer, NationalHolidaySerializer

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all().order_by('-date')
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

class LeaveRequestViewSet(viewsets.ModelViewSet):
    queryset = LeaveRequest.objects.all().order_by('-start_date')
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]

class NationalHolidayViewSet(viewsets.ModelViewSet):
    queryset = NationalHoliday.objects.all().order_by('date')
    serializer_class = NationalHolidaySerializer
    # Data hari libur mungkin hanya bisa di-read oleh user biasa, tapi 
    # di sini kita buat CRUD penuh untuk HR Admin
    permission_classes = [IsAuthenticated]