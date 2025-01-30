from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'student_number', 'grade', 'gender', 'birthday', 'head_teacher', 'get_parents')  # 显示班主任
    search_fields = ('student_name', 'student_number', 'grade__grade_name', 'contact_number', 'head_teacher__teacher_name')  # 支持按班主任名字搜索
    list_filter = ('grade', 'gender', 'head_teacher')  # 支持按班主任筛选
    readonly_fields = ('get_parents',)

    def get_parents(self, obj):
        """显示关联的保護者名字"""
        if obj.parent_names:
            return obj.parent_names
        return "未登録"
    get_parents.short_description = '保護者名'

    fieldsets = (
        ('基本情報', {
            'fields': ('student_name', 'student_number', 'grade', 'gender', 'birthday', 'contact_number', 'address', 'head_teacher')
        }),
        ('保護者情報', {
            'fields': ('get_parents',),
        }),
    )
