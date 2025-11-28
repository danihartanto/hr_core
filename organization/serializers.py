# organization/serializers.py

from rest_framework import serializers
from .models import Company, GroupHead, Department, Unit, JobTitle

# Serializer untuk level terendah hingga tertinggi
class JobTitleSerializer(serializers.ModelSerializer):
    # Field baru untuk menampilkan nilai teks dari Choices (Band 1, Band 2, dst.)
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    class Meta:
        model = JobTitle
        fields = '__all__'

class UnitSerializer(serializers.ModelSerializer):
    # Menampilkan Job Titles di bawah Unit ini (opsional)
    job_titles = JobTitleSerializer(many=True, read_only=True) 

    class Meta:
        model = Unit
        fields = '__all__'

class DepartmentSerializer(serializers.ModelSerializer):
    # Menampilkan Unit di bawah Department ini
    units = UnitSerializer(many=True, read_only=True) 
    
    class Meta:
        model = Department
        fields = '__all__'

class GroupHeadSerializer(serializers.ModelSerializer):
    # Menampilkan Department di bawah Group Head ini
    departments = DepartmentSerializer(many=True, read_only=True)
    
    class Meta:
        model = GroupHead
        fields = '__all__'

class CompanySerializer(serializers.ModelSerializer):
    # Menampilkan Group Heads di bawah Company ini
    group_heads = GroupHeadSerializer(many=True, read_only=True)
    
    class Meta:
        model = Company
        fields = '__all__'