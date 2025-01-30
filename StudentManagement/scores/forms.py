from django import forms
from django.core.exceptions import ValidationError

from .models import Score
from students.models import Student, Grade


class ScoreForm(forms.ModelForm):
    class Meta:
        model = Score
        fields = ['title', 'student_name', 'student_number', 'grade', 'japanese_score', 'math_score', 'english_score']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['grade'].queryset = Grade.objects.all()
        self.fields['grade'].empty_label = 'クラスを選択してください'

    def clean_student_number(self):
        student_number = self.cleaned_data.get('student_number')
        student_number = str(student_number)  # 确保 student_number 为字符串
        if len(student_number) != 6:
            raise ValidationError('学籍番号は6桁で入力してください')
        return student_number

    def clean_student_name(self):
        student_name = self.cleaned_data.get('student_name')
        if len(student_name) < 2 or len(student_name) > 20:
            raise ValidationError('正しい名前を入力してください')
        return student_name

    def clean(self):
        """添加综合验证逻辑"""
        cleaned_data = super().clean()
        student_name = cleaned_data.get('student_name')
        student_number = cleaned_data.get('student_number')
        grade = cleaned_data.get('grade')

        # 确保学生信息存在并与班级匹配
        try:
            student = Student.objects.get(student_name=student_name, student_number=student_number)
        except Student.DoesNotExist:
            raise ValidationError("学生情報が一致しません。名前と学籍番号を確認してください。")

        # 验证学生的班级是否匹配
        if student.grade != grade:
            raise ValidationError("学生のクラスが選択されたクラスと一致しません。")

        return cleaned_data
