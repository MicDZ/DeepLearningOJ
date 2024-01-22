from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_view, name='upload_view'),
    path('ranklist/', views.ranklist_view, name='ranklist_view'),
    path('submissions/', views.submissions_view, name='submissions_view'),
    path('submissions/<uuid:file_id>/', views.submission_detail_view, name='submission_detail_view'),
    # 添加排行榜页面的URL路由
]

