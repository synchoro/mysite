from django.db import models
from django.contrib.auth.models import User
from scores.models import Score
from students.models import Student
import re
from django.core.exceptions import ValidationError

class Parent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='parent',verbose_name='ユーザー',null=True,blank=True)
    parent_name = models.CharField(max_length=50, verbose_name='保護者名')
    phone_number = models.CharField(max_length=20, unique=True, verbose_name='電話番号')
    children = models.ManyToManyField(Student, related_name='parents', verbose_name='子供')  # 多対多の関係

    def save(self, *args, **kwargs):
        self.phone_number = re.sub(r'[-]', '', self.phone_number)
        # 如果没有关联用户，创建新的 User 对象
        if not self.user:
            username = f"{self.parent_name}_{self.phone_number}"
            password = self.phone_number[-6:]  # 默认密码为电话号码后6位
            user = User.objects.create_user(username=username, password=password)
            user.is_staff = False  # 家长不是管理员
            user.is_superuser = False  # 家长也不是超级用户
            user.save()
            self.user = user
        super().save(*args, **kwargs)

    def get_children_scores(self):
        """家長の子供たちの成績を取得"""
        return Score.objects.filter(student_number__in=[child.student_number for child in self.children.all()])
        


    def __str__(self):
        return self.parent_name
    
    class Meta:
        db_table='parent'
        verbose_name='保護者情報'
        verbose_name_plural='保護者情報'