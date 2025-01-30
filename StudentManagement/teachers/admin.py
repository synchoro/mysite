from django.contrib import admin
from .models import Teacher
from django.contrib.auth.models import User

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('teacher_name', 'user', 'formatted_phone_number', 'gender', 'birthday', 'grade')
    search_fields = ('teacher_name', 'phone_number', 'user__username', 'grade__grade_name')
    list_filter = ('gender', 'grade')
    ordering = ('grade', 'teacher_name')

    fieldsets = (
        ('基本情報', {
            'fields': ('user', 'teacher_name', 'phone_number', 'gender', 'birthday')
        }),
        ('担当情報', {
            'fields': ('grade',),
        }),
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'user':
            assigned_users = Teacher.objects.values_list('user_id', flat=True)
            kwargs['queryset'] = User.objects.exclude(id__in=assigned_users)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formatted_phone_number(self, obj):
        """電話番号を - を含む形式に"""
        phone_number = obj.phone_number.replace("-", "")
        return f"{phone_number[:3]}-{phone_number[3:7]}-{phone_number[7:]}"
    formatted_phone_number.short_description = "電話番号"
