from django.db import models
from django.contrib.auth.models import User
from grades.models import Grade

# Create your models here.

GENDER_CHOICES=(
    ('M','男性'),
    ('F','女性'),
)

class Student(models.Model):
    student_name=models.CharField(max_length=50,verbose_name='名前')
    student_number=models.CharField(max_length=20,unique=True,verbose_name='学籍番号')
    # 班级表一对多关联
    grade=models.ForeignKey(Grade,on_delete=models.CASCADE,related_name='students',verbose_name='クラス')
    gender=models.CharField(max_length=1,choices=GENDER_CHOICES,verbose_name='性別')
    birthday=models.DateField(verbose_name='生年月日',help_text='例：2001-06-29')
    contact_number=models.CharField(max_length=20,verbose_name='連絡先',help_text='※ハイフンあり')
    address=models.TextField(verbose_name='住所')

    # user表一对一关联
    user=models.OneToOneField(User,on_delete=models.CASCADE)

    

    def __str__(self)->str:
        return self.user.username
    
    class Meta:
        db_table='student'
        verbose_name='学生情報'
        verbose_name_plural='学生情報'