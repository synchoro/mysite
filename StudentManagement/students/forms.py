import datetime
import re

from django import forms
from django.core.exceptions import ValidationError

from .models import Student
from grades.models import Grade

class StudentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields.get('grade').queryset = Grade.objects.all().order_by('grade_number')

    def clean_student_name(self):
        student_name=self.cleaned_data.get('student_name')
        if len(student_name) <2 or len(student_name)>20:
            raise ValidationError('正しい名前を入力してください')
        return student_name         

    def clean_student_number(self):
        student_number=self.cleaned_data.get('student_number')
        if len(student_number)!=6:
            raise ValidationError('学籍番号は6桁で入力してください')
        return student_number
    
    def clean_birthday(self):
        birthday=self.cleaned_data.get('birthday')
        if not isinstance(birthday,datetime.date):
            raise ValidationError('生年月日の形式が正しくありません。正しい形式: YYYY-MM-DD')
        if birthday > datetime.date.today():
            raise ValidationError('生年月日は現在日より前にしてください')
        return birthday
    
    def clean_contact_number(self):
        contact_number = self.cleaned_data.get('contact_number')
        # 正規表現のルールを定義（ハイフンなしの入力を許容）
        phone_pattern = re.compile(r"^(070|080|090)(\d{4})(\d{4})$")  # 匹配没有连字符的格式
        if phone_pattern.match(contact_number):
            # ハイフンを自動的に追加
            contact_number = f"{contact_number[:3]}-{contact_number[3:7]}-{contact_number[7:]}"
        else:
            # ハイフン付きの形式を検証
            phone_pattern_with_hyphens = re.compile(r"^(070|080|090)-\d{4}-\d{4}$")
            if not phone_pattern_with_hyphens.match(contact_number):
                raise ValidationError('電話番号の形式が正しくありません。<br>（正しい形式: 090-1234-5678）')
        return contact_number

            
    class Meta:
        model=Student
        # fields = '__all__'
        fields=['student_name','student_number','grade', 'gender','birthday','contact_number','address']