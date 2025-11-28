# attendance/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AttendanceViewSet, LeaveRequestViewSet, NationalHolidayViewSet

router = DefaultRouter()
router.register(r'attendance', AttendanceViewSet)
router.register(r'leaves', LeaveRequestViewSet)
router.register(r'holidays', NationalHolidayViewSet)

urlpatterns = [
    path('', include(router.urls)),
]