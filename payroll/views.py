from django.shortcuts import render
# payroll/views.py

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Overtime, PayrollRecord
from .serializers import OvertimeSerializer, PayrollRecordSerializer

class OvertimeViewSet(viewsets.ModelViewSet):
    # Mengurutkan berdasarkan tanggal terbaru
    queryset = Overtime.objects.all().order_by('-date')
    serializer_class = OvertimeSerializer
    permission_classes = [IsAuthenticated]

class PayrollRecordViewSet(viewsets.ModelViewSet):
    # Mengurutkan berdasarkan tahun dan bulan terbaru
    queryset = PayrollRecord.objects.all().order_by('-pay_year', '-pay_month')
    serializer_class = PayrollRecordSerializer
    permission_classes = [IsAuthenticated]
