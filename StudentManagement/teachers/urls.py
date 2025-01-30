
from django.urls import path
from .views import TeacherListView, TeacherCreateView, TeacherUpdateView, TeacherDeleteView

urlpatterns = [
    path('', TeacherListView.as_view(), name='teachers_list'),
    path('teacher/create/', TeacherCreateView.as_view(), name='teacher_create'),
    path('teacher/<int:pk>/update/', TeacherUpdateView.as_view(), name='teacher_update'),
    path('teacher/<int:pk>/delete/', TeacherDeleteView.as_view(), name='teacher_delete'),
]