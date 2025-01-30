from django.db import models
from students.models import Grade

# Create your models here.
class Score(models.Model):
    title = models.CharField(max_length=20,help_text='title/試験名',verbose_name='試験名')
    student_number = models.CharField(max_length=20,verbose_name='学生番号')
    student_name = models.CharField(max_length=20,help_text='name/名前',verbose_name='名前')
    japanese_score = models.DecimalField(max_digits=5,decimal_places=0,help_text='score/国語の点数',verbose_name='国語の点数')
    math_score = models.DecimalField(max_digits=5,decimal_places=0,help_text='score/数学の点数',verbose_name='数学の点数')
    english_score = models.DecimalField(max_digits=5,decimal_places=0,help_text='score/英語の点数',verbose_name='英語の点数')
    # クラス表（一対多の関連）
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='score', verbose_name='クラス')

    def __str__(self) -> str:
        return self.title

    class Meta:
        db_table = "score"
        verbose_name_plural = "成績情報"
        verbose_name = "成績情報"
