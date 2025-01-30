from django.db import models
from django.contrib.auth.models import User
from grades.models import Grade
from teachers.models import Teacher

# Create your models here.

GENDER_CHOICES=(
    ('M','男性'),
    ('F','女性'),
)

class Student(models.Model):
    student_name=models.CharField(max_length=50,verbose_name='名前')
    student_number=models.CharField(max_length=20,unique=True,verbose_name='学籍番号')
    # クラス表（一対多の関連）
    grade=models.ForeignKey(Grade,on_delete=models.CASCADE,related_name='students',verbose_name='クラス')
    gender=models.CharField(max_length=1,choices=GENDER_CHOICES,verbose_name='性別')
    birthday=models.DateField(verbose_name='生年月日',help_text='例：2001-06-29')
    contact_number=models.CharField(max_length=20,verbose_name='連絡先',help_text='※ハイフンあり')
    address=models.TextField(verbose_name='住所')

    # ユーザー表（一対一の関連）
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    head_teacher = models.ForeignKey(Teacher,on_delete=models.SET_NULL, null=True,blank=True,related_name='students',verbose_name='担任先生')
    parent_names = models.TextField(blank=True, verbose_name='保護者名一覧') 

    

    def __str__(self)->str:
        return self.user.username
    
    class Meta:
        db_table='student'
        verbose_name='学生情報'
        verbose_name_plural='学生情報'