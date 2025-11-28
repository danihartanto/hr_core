from django.shortcuts import render

# Create your views here.
# organization/views.py

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Company, GroupHead, Department, Unit, JobTitle
from .serializers import (
    CompanySerializer, 
    GroupHeadSerializer, 
    DepartmentSerializer, 
    UnitSerializer, 
    JobTitleSerializer
)

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated] # Hanya user terautentikasi yang bisa CRUD

class GroupHeadViewSet(viewsets.ModelViewSet):
    queryset = GroupHead.objects.all()
    serializer_class = GroupHeadSerializer
    permission_classes = [IsAuthenticated]

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]

class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    permission_classes = [IsAuthenticated]

class JobTitleViewSet(viewsets.ModelViewSet):
    queryset = JobTitle.objects.all()
    serializer_class = JobTitleSerializer
    permission_classes = [IsAuthenticated]