from django.db import models

# Create your models here.
class Grade(models.Model):
    grade_name = models.CharField(max_length=50,unique=True,verbose_name='クラス名')
    grade_number=models.CharField(max_length=10,unique=True,verbose_name='クラス番号')

    def __str__(self)->str:
        return self.grade_name

    class Meta:
        db_table = 'grade'
        verbose_name = 'クラス'
        verbose_name_plural = 'クラス名'
