from django import forms
from django.core.exceptions import ValidationError


ROLE_CHOICES = [
    ('admin', '管理者'),
    ('teacher', '教師'),
    ('student', '学生'),
    ('parent', '保護者'),
]


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '電話番号または学生番号を入力してください'}),
    )
    password = forms.CharField(
        max_length=50,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'パスワードを入力してください'}),
    )

    role = forms.ChoiceField(label='役割', choices=ROLE_CHOICES)

    def clean_username(self):
        username = self.cleaned_data['username']
        if len(username) == 0:
            raise ValidationError('ユーザー名の長さは0にすることはできません。')
        return username

    def clean_password(self):
        password = self.cleaned_data['password']
        if len(password) == 0:
            raise ValidationError('パスワードは空きにすることはできません。')
        return password
    

    def clean_role(self):
        role = self.cleaned_data['role']
        if role not in ['admin', 'student', 'teacher','parent']:
            raise ValidationError('ユーザーの役割を選択してください')
        return role


