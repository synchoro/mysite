import datetime
import json
import openpyxl
from pathlib import Path
from io import BytesIO

from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView,CreateView,UpdateView,DeleteView,View
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.db.models import Q
from django.db import transaction
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

from .models import Student
from grades.models import Grade
from .forms import StudentForm
from utils.handle_excel import ReadExcel

# Create your views here.
class StudentListView(ListView):
    model = Student
    template_name = 'students/students_list.html'
    context_object_name = 'students'
    paginate_by = 10

    def get_queryset(self):
        queryset=super().get_queryset()
        grade_id=self.request.GET.get('grade') # クラスを取得
        keyword=self.request.GET.get('search') # 検索内容を取得
        if grade_id:
            queryset=queryset.filter(grade__pk=grade_id)
        if keyword:
            queryset=queryset.filter(Q(student_name__icontains=keyword)|Q(student_number__icontains=keyword))
        return queryset

    
    def get_context_data(self):
        context=super().get_context_data()
        # 全てのクラスを取得し、コンテキストに追加
        context['grades']=Grade.objects.all().order_by('grade_number')
        context['current_grade']=self.request.GET.get('grade','')
        return context


class StudentCreateView(CreateView):
    model=Student
    template_name = 'students/student_form.html'
    form_class=StudentForm

    def form_valid(self, form):
        # 検証を通過したフィールドの値を取得
        student_name=form.cleaned_data.get('student_name')
        student_number = form.cleaned_data.get('student_number')
        # auth_userテーブルに書き込み
        username=student_name+'_'+student_number
        password=student_number[-6:]
        users=User.objects.filter(username=username)
        if users.exists():
            user=users.first()
        else:
            # auth_userテーブルのレコードを作成
            # create_userは自動的に暗号化するため、平文をそのまま渡せばよい
            user=User.objects.create_user(username=username, password=password)
        # studentに書き込み
        form.instance.user=user
        form.save()

        # JSONレスポンスを返す
        return JsonResponse({
            'status':'success',
            'messages':'操作成功',
        },status=200)
    
    def form_invalid(self, form):
        errors=form.errors.as_json()
        # print(f"Form errors: {form.errors}")
        
        return JsonResponse({
            'status':'error',
            'messages':errors,
        }, status=400)

class StudentUpdateView(UpdateView):
    model=Student
    template_name = 'students/student_form.html'
    form_class=StudentForm

    def form_valid(self, form):
        # 学生オブジェクトのインスタンスを取得
        student=form.save(commit=False)
        # student_nameまたはstudent_numberが変更されたかどうかを確認
        if 'student_name' in form.changed_data or 'student_number' in form.changed_data:
            student.user.username=form.cleaned_data.get('student_name')+'_'+form.cleaned_data.get('student_number')
            student.user.password=make_password(form.cleaned_data.get('student_number')[-6:])
            student.user.save()
        # studentモデルを保存
        student.save()

        # JSONレスポンスを返す
        return JsonResponse({
            'status':'success',
            'messages':'操作成功',
        },status=200)

    def form_invalid(self, form):
        errors=form.errors.as_json()
        print(form.errors)  # コンソールに具体的なエラーログを出力
        return JsonResponse({
            'status':'error',
            'messages':errors,
        }, status=400)
    

class StudentDeleteView(DeleteView):
    success_url=reverse_lazy('student_list')
    model = Student
    # 親クラスの削除メソッドをオーバーライド
    def delete(self, request, *args, **kwargs):
        try:
            # 削除対象のオブジェクトを取得する
            self.object = self.get_object()
            # オブジェクトを削除する
            self.object.delete()
            return JsonResponse({
                'status': 'success',
                'messages': '操作成功',
            }, status=200)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'messages': f'削除失敗: {str(e)}',
            }, status=500)
        

class StudentBulkDeleteView(DeleteView):
    model = Student
    success_url =reverse_lazy('student_list')
    def post(self,request,*args,**kwargs):
        selected_ids = request.POST.getlist('student_ids')
        if not selected_ids:
            return JsonResponse({
                'status': 'error',
                'messages': '削除する学生情報を選択してください'
            }, status=400)

        self.object_list = self.get_queryset().filter(id__in=selected_ids)
        try:
            self.object_list.delete()
            return JsonResponse({
                'status': 'success',
                'messages': '削除成功'
            }, status=200)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'messages': f'削除失敗: {str(e)}',
            }, status=500)

def upload_student(request):
    if request.method == 'POST':
        file = request.FILES.get('excel_file')
        if not file:
            return JsonResponse({
                'status': 'error',
                'messages': 'ファイルを選択してください'
            }, status=400)

        # ファイル拡張子が.xlsxかどうかを確認
        ext = Path(file.name).suffix
        if ext.lower() not in ['.xlsx']:
            return JsonResponse({
                'status': 'error',
                'messages': 'アップロードできるのは「.xlsx」のExcelファイルです'
            }, status=400)

        # openpyxlを使用してExcelファイルを読み込む
        try:
            read_excel = ReadExcel(file)
            data = read_excel.get_data()
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'messages': f'Excelファイルの読み取りに失敗しました: {str(e)}'
            }, status=400)

        # ヘッダーが正しいかを検証
        if data[0] != ['クラス', '名前', '学籍番号', '性別', '生年月日', '電話番号', '住所']:
            return JsonResponse({
                'status': 'error',
                'messages': 'アップロードするExcelの学生情報が指定された形式ではありません'
            }, status=400)

        # データベースに書き込みを開始
        try:
            with transaction.atomic():
                for row in data[1:]:
                    grade_name, student_name, student_number, gender, birthday, contact_number, address = row
                    
                    # クラスが存在するかを確認
                    grade = Grade.objects.filter(grade_name=grade_name).first()
                    if not grade:
                        return JsonResponse({
                            'status': 'error',
                            'messages': f'{grade_name}というクラスは存在していません'
                        }, status=400)

                    # 学生情報の検証
                    if not student_name:
                        return JsonResponse({'status': 'error', 'messages': '学生の名前は空にできません'}, status=400)

                    if not student_number or len(str(student_number)) != 6:
                        return JsonResponse({
                            'status': 'error',
                            'messages': '学籍番号は空にできず、長さは6文字でなければなりません'
                        }, status=400)

                    if not isinstance(birthday, datetime.date):
                        return JsonResponse({
                            'status': 'error',
                            'messages': '生年月日の形式が正しくありません'
                        }, status=400)

                    if Student.objects.filter(student_number=student_number).exists():
                        return JsonResponse({
                            'status': 'error',
                            'messages': f'学籍番号{student_number}は既に存在しています'
                        }, status=400)

                    # ユーザーと学生データをデータベースに書き込み
                    username = f"{student_name}_{student_number}"
                    user = User.objects.filter(username=username).first()
                    if not user:
                        password = str(student_number)[-6:]  # デフォルトのパスワードは学籍番号の最後の6文字
                        user = User.objects.create_user(username=username, password=password)

                    Student.objects.create(
                        student_name=student_name,
                        student_number=student_number,
                        grade=grade,
                        gender='M' if gender == '男性' else 'F',
                        birthday=birthday,
                        contact_number=contact_number,
                        address=address,
                        user=user
                    )

        except Exception as e:
            # データベース操作中の例外をキャッチ
            return JsonResponse({'status': 'error', 'messages': f'アップロード失敗: {str(e)}'}, status=400)

        # 全てが成功した場合に成功メッセージを返す
        return JsonResponse({'status': 'success', 'messages': 'アップロード成功'}, status=200)

    # GETリクエストまたはその他のリクエストを処理
    elif request.method == 'GET':
        return JsonResponse({
            'status': 'error',
            'messages': 'GETリクエストはサポートされていません'
        }, status=405)  # 405 = Method Not Allowed

    return HttpResponseNotAllowed(['POST'])


def export_excel(request):
    if request.method == 'POST':
        data=json.loads(request.body)
        grade_id=data.get('grade')
        # grade_idが存在するかどうかを判断する
        if not grade_id:
            return JsonResponse({
                'status': 'error',
                'messages': 'クラスIDが指定されていません'
            }, status=400)
        # クラスが存在するかどうかを判断する
        try:
            grade=Grade.objects.get(id=grade_id)
        except Grade.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'messages': f'ID={grade_id}のクラスが存在しません'
            }, status=404)
        
        # データベースから学生データをクエリする
        students=Student.objects.filter(grade=grade)
        if not students.exists():
            return JsonResponse({
                'status': 'error',
                'messages': f'ID={grade_id}のクラスには登録された学生が存在しません'
            }, status=404)
        
        # excelを操作
        wb=openpyxl.Workbook()
        ws=wb.active

        columns=['クラス', '名前', '学籍番号', '性別', '生年月日', '電話番号', '住所']
        ws.append(columns)
        for student in students:
            if student.gender=='M':
                student.gender='男性'
            else:
                student.gender='女性'
            ws.append([student.grade.grade_name,student.student_name,student.student_number,student.gender,student.birthday,student.contact_number,student.address])

        # Excelデータをメモリに保存
        excel_file=BytesIO()
        wb.save(excel_file)
        wb.close()

        # ファイルポインタをリセットし、ファイルの先頭に移動
        excel_file.seek(0)

        # レスポンスを設定
        response=HttpResponse(excel_file.read(),content_type='application/vnd.openxmlformats-officedocument.spreadsheetml')
        # 添付ファイルとしてリクエスト側に送信
        response['Content-Disposition']="attachment; filename='students.xlsx'"
        return response







