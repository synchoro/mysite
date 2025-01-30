import re
from django.db import models
from django.contrib.auth.models import User
from grades.models import Grade


# Create your models here.
GENDER_CHOICES = [
    ('M', '男性'),
    ('F', '女性'),
]

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher',verbose_name='ユーザー',null=True,blank=True)
    teacher_name = models.CharField(max_length=50, verbose_name='教師名')
    phone_number = models.CharField(max_length=20, unique=True, verbose_name='電話番号',help_text='※ハイフンあり')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name='性別')
    birthday = models.DateField(verbose_name='生年月日', help_text='例：1996-06-02') 
    grade = models.OneToOneField(Grade, on_delete=models.DO_NOTHING, verbose_name='担当クラス')

    def clean_phone_number(self):
        """電話番号から '-' を削除"""
        return self.phone_number.replace("-", "")
    
    def get_formatted_phone_number(self):
        """電話番号を - を含む形式に"""
        phone_number = self.phone_number.replace("-", "")
        return f"{phone_number[:3]}-{phone_number[3:7]}-{phone_number[7:]}"

    def __str__(self) -> str:
        return self.teacher_name

    class Meta:
        db_table = "teacher"
        verbose_name_plural = "教師情報"
        verbose_name = "教師情報"
