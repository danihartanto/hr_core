from rest_framework import permissions
from users.models import SystemUser

class IsSuperuser(permissions.BasePermission):
    """
    Memberikan izin hanya jika user yang melakukan request adalah Superuser Django.
    """
    def has_permission(self, request, view):
        return request.user.is_superuser
    
class IsSystemAdminOrSuperuser(permissions.BasePermission):
    """
    Memberikan izin hanya jika user adalah Superuser Django 
    atau memiliki SystemUser.level_user sebagai 'ADM' (Administrator).
    USER_LEVEL_CHOICES = (
        ('employee', 'Employee Basic'),
        ('staff', 'HR Staff'),
        ('manager', 'Manager'),
        ('admin', 'System Administrator'),
    )
    """
    def has_permission(self, request, view):
        user = request.user
        
        # 1. Izinkan akses jika user adalah Superuser Django
        if user.is_superuser:
            return True
        
        # 2. Cek user yang terhubung ke SystemUser
        try:
            system_user = SystemUser.objects.get(user=user)
            # Izinkan jika level user adalah Administrator ('ADM') atau HR
            if system_user.level_user in ['admin', 'manager']:
                 return True
        except SystemUser.DoesNotExist:
            # Jika user terotentikasi tetapi tidak memiliki SystemUser (non-admin), tolak
            return False 
            
        return False