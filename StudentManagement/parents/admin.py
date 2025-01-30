from django.contrib import admin
from .models import Parent


@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ('parent_name', 'phone_number', 'get_user_username', 'get_children_names')
    search_fields = ('parent_name', 'phone_number', 'user__username')
    filter_horizontal = ('children',)

    def get_children_names(self, obj):
        """显示关联的孩子的名字"""
        return ', '.join([child.student_name for child in obj.children.all()])
    get_children_names.short_description = '子供たち'

    def get_user_username(self, obj):
        """在列表中显示关联用户的用户名"""
        return obj.user.username if obj.user else "未关联"
    get_user_username.short_description = "ユーザー名"
