from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from django.db.models import Q

from .forms import TeacherForm
from .models import Teacher
from grades.models import Grade

class BaseTeacherView():
    model = Teacher
    success_url = reverse_lazy('teachers_list')  # 作成成功後のリダイレクトURL    

class TeacherListView(BaseTeacherView, ListView):
    template_name = 'teachers/teachers_list.html'
    context_object_name = 'teachers'
    paginate_by = 10  # 1ページあたりの表示件数

    def get_queryset(self):
        queryset = super().get_queryset()
        grade_id = self.request.GET.get('grade') # クラスを取得
        keyword = self.request.GET.get('search') # 検索内容を取得
        if grade_id:
            queryset = queryset.filter(grade__pk=grade_id)
        if keyword:
            queryset = queryset.filter(
                Q(phone_number=keyword) |
                Q(teacher_name=keyword)
            )
        return queryset

    def get_context_data(self):
        context = super().get_context_data()
        # 全てのクラスを取得してコンテキストに追加
        context['grades'] = Grade.objects.all().order_by('grade_number')
        context['current_grade'] = self.request.GET.get('grade', '')
        return context

class TeacherCreateView(BaseTeacherView, CreateView):
    form_class = TeacherForm
    template_name = 'teachers/teacher_form.html'
    context_object_name = 'teachers'

    def form_valid(self, form):
        # フォームからユーザー情報を取得
        teacher_name = form.cleaned_data.get('teacher_name')  # フォームに教師名があることを仮定
        phone_number = form.cleaned_data.get('phone_number')  # フォームに電話番号があることを仮定
        clean_phone_number = phone_number.replace("-", "")


        # auth_userテーブルに教師データが存在するかを確認し、存在しない場合は新規作成
        username = teacher_name + '_' + clean_phone_number # ユーザー名の結合
        users = User.objects.filter(username=username)
        if users.exists():
            # Userオブジェクトを取得
            user = users.first()
        else:
            # Userオブジェクトを作成
            password = clean_phone_number[-6:]
            user = User.objects.create_user(username=username, password=password)
            
        # 新規作成したユーザーをTeacherインスタンスに関連付け
        form.instance.user = user
        # Teacherインスタンスを保存
        form.save()
        # JSONレスポンスを返す
        return JsonResponse({
            'status': 'success',
            'messages': '操作が成功しました',
        })
    
    def form_invalid(self, form):
        # エラー情報を返す
        errors = form.errors.as_json()
        return JsonResponse({'status': 'error', 'messages': errors}, status=400)


class TeacherUpdateView(BaseTeacherView, UpdateView):
    form_class = TeacherForm
    template_name = 'teachers/teacher_form.html'

    def form_valid(self, form):
        teacher = form.save(commit=False)
        if 'teacher_name' in form.changed_data or 'phone_number' in form.changed_data:
            # '-' を削除して内部処理用に変更
            clean_phone_number = form.cleaned_data['phone_number'].replace("-", "")
            teacher.user.username = f"{form.cleaned_data['teacher_name']}_{clean_phone_number}"
            teacher.user.set_password(clean_phone_number[-6:])  # 新しいパスワードを設定
            teacher.user.save()
        teacher.save()
        return JsonResponse({
            'status': 'success',
            'message': '操作が成功しました',
        })
    
    def form_invalid(self, form):
        # エラー情報を返す
        errors = form.errors.as_json()
        return JsonResponse({'status': 'error', 'messages': errors}, status=400)

class TeacherDeleteView(BaseTeacherView, DeleteView):

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        if response.status_code == 302:
            return JsonResponse({'status': 'success', 'messages': '教師が削除されました'})
        else:
            return JsonResponse({'status': 'error', 'messages': '削除に失敗しました'}, status=400)
