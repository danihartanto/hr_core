# attendance/serializers.py

from rest_framework import serializers
from .models import Attendance, LeaveRequest, NationalHoliday

# --- Attendance Serializer ---
class AttendanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    
    class Meta:
        model = Attendance
        fields = '__all__'
        
# --- Leave Request Serializer ---
class LeaveRequestSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    # Menampilkan tipe dan status cuti dalam format teks
    leave_type_display = serializers.CharField(source='get_leave_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = LeaveRequest
        fields = '__all__'
        
# --- National Holiday Serializer ---
class NationalHolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = NationalHoliday
        fields = '__all__'