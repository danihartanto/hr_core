# payroll/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OvertimeViewSet, PayrollRecordViewSet

router = DefaultRouter()
router.register(r'overtimes', OvertimeViewSet)
router.register(r'records', PayrollRecordViewSet)

urlpatterns = [
    path('', include(router.urls)),
]