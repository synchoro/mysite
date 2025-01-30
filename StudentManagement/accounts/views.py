from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash


from .forms import LoginForm
from teachers.models import Teacher
from students.models import Student
from parents.models import Parent

# Create your views here.
def user_login(request):
    # POSTリクエストかどうかを確認
    if request.method == 'POST':
        # フォームバリデーション
        form = LoginForm(request.POST)
        # バリデーション失敗
        if not form.is_valid():
            return JsonResponse({'status': 'error', 'messages': '送信情報に誤りがあります！'}, status=400, safe=False)
        # バリデーション成功
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        role = form.cleaned_data.get('role')
        # 役割を判定
        if role == 'teacher':
            try:
                teacher = Teacher.objects.get(phone_number=username)
                username = teacher.teacher_name + '_' + teacher.phone_number
                user = authenticate(username=username, password=password)
                # teacher.user.username 
            except Teacher.DoesNotExist:
                return JsonResponse({'status': 'error', 'messages': '教師情報が存在しません'}, status=404)
        elif role == 'student':
            try:
                student = Student.objects.get(student_number=username)
                username = student.student_name + "_" + student.student_number
                user = authenticate(username=username, password=password)
            except:
                return JsonResponse({'status': 'error', 'messages': '学生情報が存在しません'}, status=404)
        elif role == 'parent':  # 保護者の処理
            try:
                parent = Parent.objects.get(phone_number=username)
                username = parent.parent_name + '_' + parent.phone_number
                user = authenticate(username=username, password=password)
                if user:
                    children = parent.children.all()
                    request.session['children'] = [child.student_name for child in children]  # 子供たちの名前をセッションに保存
            except Parent.DoesNotExist:
                return JsonResponse({'status': 'error', 'messages': '保護者情報が存在しません'}, status=404)
        else:
            try:
                user = authenticate(username=username, password=password)
            except:
                return JsonResponse({'status': 'error', 'messages': '管理者情報が存在しません'}, status=404)
        # 認証成功時にJSONデータを返す
        if user is not None:
            if user.is_active:
                login(request, user)
                request.session['username'] = username.split('_')[0]
                request.session['user_role'] = role
                return JsonResponse({'status': 'success', 'messages': 'ログイン成功', 'role': role})
            else:
                return JsonResponse({'status': 'error', 'messages': 'アカウントが無効化されています'}, status=403)
        else:
            # ログイン失敗時の処理
            return JsonResponse({'status': 'error', 'messages': 'ユーザー名またはパスワードが正しくありません'}, status=401)  
        

    return render(request, 'accounts/login.html')


def user_logout(request):
    """ログアウト"""
    if 'user_role' in request.session:
        del request.session['user_role']
    logout(request)  # ログアウトを実行
    # すべてのセッションを削除
    request.session.flush()
    return redirect('user_login')

def change_password(request):
    if request.method == 'POST':
        form=PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user=form.save()
            update_session_auth_hash(request, user)  
            return JsonResponse({'status':'success','messages':'パスワードが変更されました'})
        else:
            errors=form.errors.as_json()
            return JsonResponse({'status':'error','messages':errors}, status=400)
    return render(request, 'accounts/change_password.html')

def error_404_view(request, exception):
    return render(request, '404.html', {}, status=404)

