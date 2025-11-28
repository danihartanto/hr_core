from django.contrib import admin
from .models import Company, GroupHead, Department, Unit, JobTitle

# --- INLINE (Untuk melihat/mengedit model anak dari model induk) ---

class GroupHeadInline(admin.TabularInline):
    model = GroupHead
    extra = 1  # Jumlah form kosong yang ditampilkan

class DepartmentInline(admin.TabularInline):
    model = Department
    extra = 1

class UnitInline(admin.TabularInline):
    model = Unit
    extra = 1

class JobTitleInline(admin.TabularInline):
    model = JobTitle
    extra = 1

# --- PENDAFTARAN MODEL UTAMA ---

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'legal_name')
    search_fields = ('name',)
    # Tampilkan GroupHead yang dimiliki Company ini
    inlines = [GroupHeadInline] 

@admin.register(GroupHead)
class GroupHeadAdmin(admin.ModelAdmin):
    list_display = ('name', 'company')
    list_filter = ('company',)
    search_fields = ('name',)
    # Tampilkan Department yang dimiliki GroupHead ini
    inlines = [DepartmentInline]

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'group_head')
    list_filter = ('group_head',)
    search_fields = ('name',)
    # Tampilkan Unit yang dimiliki Department ini
    inlines = [UnitInline]

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('name', 'department')
    list_filter = ('department',)
    search_fields = ('name',)
    # Tampilkan JobTitle yang dimiliki Unit ini
    inlines = [JobTitleInline]

@admin.register(JobTitle)
class JobTitleAdmin(admin.ModelAdmin):
    list_display = ('title_name', 'unit', 'level', 'level_name')
    list_filter = ('unit', 'level')
    search_fields = ('title_name',)
