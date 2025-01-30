from pathlib import Path
import json
from io import BytesIO

from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse
from django.db import transaction
from django.db.models import Q
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
import openpyxl

from .forms import ScoreForm
from .models import Score
from students.models import Student, Grade
from utils.handle_excel import ReadExcel
from utils.permissions import RoleRequiredMixin, role_required


@transaction.atomic
def upload_student_scores(file):
    # Excelデータを取得
    upload = ReadExcel(file) 
    data = upload.get_data()
    # ヘッダーを取得
    if data[0] != ['試験名', 'クラス', '名前', '学籍番号', '国語の成績', '数学の成績', '英語の成績']:
        return {'status': 'error', 'messages': 'Excelのフォーマットが正しくありません'}
    
    # 内容データを取得
    for row in data[1:]:
        title, grade_name, student_name, student_number, japanese_score, math_score, english_score = row  # 1列目が名前、2列目が電話番号と仮定
        if not student_name:
            return {'status': 'error', 'messages': '学生の名前は必須です'}
        if not student_number or len(str(student_number)) != 6:
            return {'status': 'error', 'messages': '学籍番号は必須で、長さは6文字である必要があります'}
        # クラス名が存在するか確認し、教師がそのクラス情報をアップロードできるか確認
        grade = Grade.objects.filter(grade_name=grade_name).first()
        if not grade:
            return {'status': 'error', 'messages': f'クラス名"{grade_name}"が存在しません'}

        # 学生情報が存在するか確認
        try:
            Student.objects.get(
                student_name=student_name,
                student_number=student_number,
                grade=grade
            )
        except Student.DoesNotExist:
            return {'status': 'error', 'messages': '学生情報が存在しません'}

        # scoreテーブルにレコードを作成
        Score.objects.create(
            title=title,
            student_name=student_name, 
            student_number=student_number,
            grade=grade,
            japanese_score=japanese_score,
            math_score=math_score,
            english_score=english_score
        )
    return {'status': 'success', 'messages': 'ファイルアップロードが成功しました'}


@role_required('admin', 'teacher')  
def upload_scores(request):
    if request.method == 'POST':
        file = request.FILES.get('excel_file')
        if not file:
            return JsonResponse({'status': 'error', 'messages': 'Excelファイルをアップロードしてください'}, status=400)
        # ファイル形式がxlsxかどうか確認
        ext = Path(file.name).suffix
        if ext.lower() != '.xlsx':
            return JsonResponse({'status': 'error', 'messages': 'ファイル形式が間違っています。xlsx形式のファイルをアップロードしてください'}, status=400)
        
        # openpyxlを使用してExcelファイルを処理
        result = upload_student_scores(file)
        return JsonResponse(result)
        
    return JsonResponse({'error': '無効なリクエスト'}, status=400)    


@role_required('admin', 'teacher')  
def export_scores(request):
    """Excelをエクスポート"""
    if request.method == 'POST':
        data = json.loads(request.body)
        grade_id = data.get('grade')

        # クラスパラメータを受け取る
        if not grade_id:
            return JsonResponse({'status': 'error', 'messages': 'クラスパラメータが不足しています'}, status=400)
        
        # クラスが存在するか確認
        try:
            grade = Grade.objects.get(id=grade_id)
        except Grade.DoesNotExist:
            return JsonResponse({'status': 'error', 'messages': 'クラスが存在しません'}, status=404)
        
        # データベースから学生のデータを取得
        scores = Score.objects.filter(grade=grade)
        if not scores.exists():
            return JsonResponse({'status': 'error', 'messages': '指定されたクラスの成績情報が見つかりません'}, status=404)

        # Excelワークブックを作成
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = 'Score'

        # タイトル行を追加
        columns = ['試験名', 'クラス', '名前', '学籍番号', '国語の成績', '数学の成績', '英語の成績']
        ws.append(columns)

        # データ行を追加
        for score in scores:
            ws.append([score.title, score.grade.grade_name, score.student_name, score.student_number, score.japanese_score, score.math_score, score.english_score])

        # Excelワークブックをメモリに保存
        excel_file = BytesIO()
        wb.save(excel_file)
        wb.close()

        # ファイルポインタをリセット
        excel_file.seek(0)

        # レスポンスを設定
        response = HttpResponse(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="students.xlsx"'
        return response


class BaseScoreView(RoleRequiredMixin):
    model = Score
    success_url = reverse_lazy('score_list')  # 作成成功後にリダイレクトされるURL
    allowed_roles = ['admin', 'teacher']  # 許可される役割を設定


# ビューを作成
class ScoreListView(BaseScoreView, ListView):
    template_name = 'scores/score_list.html'
    context_object_name = 'scores'
    paginate_by = 10  # 1ページに10件表示

    def get_queryset(self):
        queryset = super().get_queryset()

        # **クラス（班級）フィルタリングのパラメータを取得**
        grade_query = self.request.GET.get('grade')  # クラスフィルタのパラメータ
        if grade_query:
            queryset = queryset.filter(grade__pk=grade_query)

        # **検索パラメータを取得**
        search_query = self.request.GET.get('search')  # 検索クエリ
        if search_query:
            queryset = queryset.filter(
                Q(student_number__icontains=search_query) | 
                Q(student_name__icontains=search_query)
            )

        # **ソートパラメータを取得、デフォルトは ID 順**
        sort_by = self.request.GET.get('sort_by', 'id')  # デフォルトのソートフィールド
        valid_sort_fields = {
            'japanese': '-japanese_score',  # 国語の降順
            'math': '-math_score',         # 数学の降順
            'english': '-english_score',   # 英語の降順
            'id': 'id',                    # デフォルトは ID の昇順
        }
        sort_field = valid_sort_fields.get(sort_by, 'id')  # 有効なソートフィールドを取得、デフォルトは ID

        # **ソートフィールドをクエリセットに適用**
        queryset = queryset.order_by(sort_field)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 現在のクラスフィルタのパラメータをテンプレートに渡す
        context['current_grade'] = self.request.GET.get('grade', '')  # 現在のクラス
        # 現在のソートフィールドをテンプレートに渡す
        context['current_sort'] = self.request.GET.get('sort_by', 'id')  # 現在のソートフィールド
        return context



# ScoreCreateView, ScoreUpdateView, ScoreDeleteView, ScoreDeleteMultipleView
class ScoreCreateView(BaseScoreView, CreateView):
    form_class = ScoreForm
    template_name = 'scores/score_form.html'  # 使用するテンプレートファイルを指定

    def form_valid(self, form):
        # フォームからユーザー情報を取得
        student_name = form.cleaned_data.get('student_name')  # フォームから学生名を取得
        student_number = form.cleaned_data.get('student_number')  # フォームから学籍番号を取得
        grade_id = form.cleaned_data.get('grade')
        
        # 学生テーブルを検索
        try:
            student = Student.objects.get(
                student_name=student_name,
                student_number=student_number,
                grade=grade_id
            )
        except Student.DoesNotExist:
            errors = {'general': [{'message': '学生情報が存在しません', 'code': 'not_found'}]}
            return JsonResponse({'status': 'error', 'messages': errors}, status=404)

        # フォームのインスタンスを保存
        form.save()
        # JSONレスポンスを返す
        return JsonResponse({
            'status': 'success',
            'messages': '操作が成功しました',
        })
    
    def form_invalid(self, form):
        # フォームエラーを構造化されたJSON形式に変換
        errors = {field: [{'message': error, 'code': ''} for error in errors_list] for field, errors_list in form.errors.items()}
        return JsonResponse({'status': 'error', 'messages': errors}, status=400)


class ScoreUpdateView(BaseScoreView, UpdateView):
    form_class = ScoreForm
    template_name = 'scores/score_form.html'  # 使用するテンプレートファイルを指定

    def form_valid(self, form):
        # フォームから学生インスタンスを取得
        form.save()
        # JSONレスポンスを返す
        return JsonResponse({
            'status': 'success',
            'messages': '操作が成功しました',
        })

    def form_invalid(self, form):
        # エラーメッセージを返す
        errors = {field: [{'message': error, 'code': ''} for error in errors_list] for field, errors_list in form.errors.items()}
        return JsonResponse({'status': 'error', 'messages': errors}, status=400)


class ScoreDetailView(DetailView):
    model = Score
    template_name = 'scores/score_detail.html'


class ScoreDeleteView(BaseScoreView, DeleteView):

    def delete(self, request, *args, **kwargs):
        # ここでAJAXリクエストかどうかを確認
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            response = super().delete(request, *args, **kwargs)
            if response.status_code == 302:  # 削除成功
                return JsonResponse({'status': 'success', 'messages': '学生が削除されました'})
            else:
                return JsonResponse({'status': 'error', 'messages': '削除に失敗しました'}, status=400)
        else:
            return super().delete(request, *args, **kwargs)

class ScoreDeleteMultipleView(BaseScoreView, DeleteView):

    def post(self, request, *args, **kwargs):
        print('POST操作を実行')
        selected_ids = request.POST.getlist('score_ids')
        if not selected_ids:
            return JsonResponse({'status': 'error', 'messages': '削除する成績を選択してください'})
        print('選択されたIDを取得')
        print(selected_ids)
        try:
            self.object_list = self.get_queryset().filter(id__in=selected_ids)
            self.object_list.delete()
        except Exception as e:
            print(e)
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest' or self.request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'messages': '成績が削除されました'})
        else:
            return self.get_success_url()
        

class MyScoreListView(BaseScoreView, ListView):
    model = Score
    template_name = 'scores/my_score_list.html'  # 使用するテンプレートファイルを指定
    context_object_name = 'scores'
    paginate_by = 10  # 1ページに10件表示
    allowed_roles = ['admin', 'teacher', 'student','parent']

    def get_queryset(self):
        # 現在のユーザーの成績のみを返す
        # student_number = self.request.user.student.student_number
        # return Score.objects.filter(student_number=student_number)
    
        
        user = self.request.user

        # 如果是学生，返回该学生的成绩
        if hasattr(user, 'student'):  # 检查用户是否关联学生
            student_number = user.student.student_number
            return Score.objects.filter(student_number=student_number)

        # 如果是家长，返回其子女的成绩
        if hasattr(user, 'parent'):  # 检查用户是否关联家长
            children = user.parent.children.all()  # 获取家长关联的所有子女
            return Score.objects.filter(student_number__in=[child.student_number for child in children])