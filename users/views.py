from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import UserProfileUpdateSerializer, PasswordResetSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from users.models import SystemUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from .permissions import IsSystemAdminOrSuperuser, IsSuperuser

# Create your views here.
# users/views.py

from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    View yang menggunakan CustomTokenObtainPairSerializer.
    """
    serializer_class = CustomTokenObtainPairSerializer

class UserListViewSet(viewsets.ModelViewSet): 
    """
    Menampilkan daftar semua pengguna dan mengizinkan CRUD 
    (dibatasi hanya untuk Admin/Superuser).
    """
    queryset = User.objects.all().order_by('username')
    
    # Gunakan serializer yang menampilkan detail User + SystemUser
    serializer_class = UserProfileUpdateSerializer 
    
    # --- TERAPKAN PERMISSION KUSTOM ---
    permission_classes = [IsSystemAdminOrSuperuser] 
    
    # Kita menggunakan JWTAuthentication karena ini adalah API
    authentication_classes = [JWTAuthentication]
    
    # reset password by superadmin only
    @action(detail=True, methods=['POST'], permission_classes=[IsSuperuser], url_path='reset-password')
    def reset_password(self, request, pk=None):
        
        # 1. Ambil objek user yang akan direset
        try:
            user_to_reset = self.get_queryset().get(pk=pk)
        except User.DoesNotExist:
            return Response(
                {"detail": "Pengguna tidak ditemukan."}, 
                status=status.HTTP_404_NOT_FOUND
            )

        # 2. Tentukan password default BARU
        # SAMAKAN password default dengan username
        DEFAULT_PASSWORD = user_to_reset.username 

        # 3. Reset password dan simpan
        user_to_reset.set_password(DEFAULT_PASSWORD)
        user_to_reset.save()

        return Response(
            {"detail": f"Password untuk '{user_to_reset.username}' berhasil direset dan disamakan dengan username."}, 
            # Tidak menampilkan password default di response (demi keamanan)
            status=status.HTTP_200_OK
        )
    
    
class UserProfileViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserProfileUpdateSerializer
    # authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Memastikan user hanya bisa melihat/mengedit profilnya sendiri
        return self.request.user 
    
    # Endpoint: GET /api/v1/users/me/
    @action(detail=False, methods=['GET'], url_path='user')
    def retrieve_profile(self, request):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        # Mengembalikan data lengkap user + SystemUser (untuk display)
        data = serializer.data
        try:
            system_user = instance.systemuser
            data['level_user'] = system_user.get_level_user_display()
            data['user_status'] = system_user.user_status
        except SystemUser.DoesNotExist:
            data['level_user'] = 'System Administrator'
            data['user_status'] = instance.is_active

        return Response(data)

    # Endpoint: PUT/PATCH /api/v1/users/me/
    # @action(detail=False, methods=['PUT', 'PATCH'], url_path='me')
    @action(detail=False, methods=['GET', 'PUT', 'PATCH'], url_path='me')
    def me(self, request):
        instance = self.get_object()
        
        # Logika GET (Retrieve)
        if request.method == 'GET':
            serializer = self.get_serializer(instance)
            # Logika penambahan data SystemUser untuk display (sama seperti sebelumnya)
            data = serializer.data
            try:
                system_user = instance.systemuser
                data['level_user'] = system_user.get_level_user_display()
                data['user_status'] = system_user.user_status
            except SystemUser.DoesNotExist:
                data['level_user'] = 'System Administrator'
                data['user_status'] = instance.is_active
            return Response(data)

        # Logika PUT / PATCH (Update)
        elif request.method in ['PUT', 'PATCH']:
            # Gunakan partial=True untuk PATCH
            partial = request.method == 'PATCH'
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        # Seharusnya tidak tercapai
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    # Endpoint: POST /api/v1/users/reset_password/
    # reset password by self user
    @action(detail=False, methods=['POST'], url_path='reset-password')
    def reset_password(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = self.request.user
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']

        # Verifikasi password lama
        if not user.check_password(old_password):
            return Response(
                {"old_password": ["Password lama salah."]}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Atur password baru
        user.set_password(new_password)
        user.save()

        return Response({"detail": "Password berhasil diubah."}, status=status.HTTP_200_OK)