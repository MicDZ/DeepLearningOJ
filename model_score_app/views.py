# model_score_app/views.py
from django.shortcuts import render, redirect
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib import messages
from django.http import HttpResponseBadRequest
from .score_model import score_model
from .models import ModelScore, FileUpload
from django.db.models import Max
import uuid
from django.utils import timezone
import pytz
from django.http import JsonResponse

def upload_view(request):
    file_id = str(uuid.uuid4())
    if request.method == 'POST':
        # 获取姓名
        username = request.POST.get('username')
        if not username:
            return
        if 'model_file' in request.FILES:
            model_file = request.FILES['model_file']

            if ModelScore.objects.filter(id=file_id).exists():
                # 如果记录已存在，则返回错误信息
                return
            # 检查文件是否符合预期格式和大小等（如果需要）
            if not model_file.name.endswith('.pt'):
                return
            # filename = default_storage.save(model_file.name, ContentFile(model_file.read()))
            print(model_file.name)
            # 将模型读取为pt文件
            upload=ModelScore(username=username, score=0, status='Running', id=file_id, file=model_file)
            upload.save()

            # return redirect('model_list')  # 假设你有一个显示模型列表的页面
        else:
            return
        # 模型评分
        print("Start to score model")
        score_model.delay(file_id)

        # 跳转到提交详情页面
        return redirect('submission_detail_view', file_id=file_id)
    # 返回
    return render(request, 'model_score/upload.html')


def ranklist_view(request):
   # 获取每个用户的最高分及对应的上传时间
   highest_scores = ModelScore.objects.values('username').annotate(max_score=Max('score'), max_upload_time=Max('upload_time')).order_by('-max_score')


   # 将结果转换为易于渲染的列表
   ranked_users = []
   for score in highest_scores:
       uploaded_at_in_utc = score['max_upload_time']
       beijing_tz = pytz.timezone('Asia/Shanghai')
       uploaded_at_in_bj = uploaded_at_in_utc.astimezone(beijing_tz)
       ranked_users.append({
           'username': score['username'],
           'score': score['max_score'],
           'upload_time': uploaded_at_in_bj.strftime("%m-%d %H:%M"),
       })

   context = {
       'scores': ranked_users,
   }
   return render(request, 'model_score/ranklist.html', context)


def submissions_view(request):
    highest_scores = ModelScore.objects.values('username', 'score', 'upload_time', 'status', 'id').order_by('-upload_time')

   # 将结果转换为易于渲染的列表
    ranked_users = []
    for score in highest_scores:
        uploaded_at_in_utc = score['upload_time']
        beijing_tz = pytz.timezone('Asia/Shanghai')
        uploaded_at_in_bj = uploaded_at_in_utc.astimezone(beijing_tz)
        ranked_users.append({
            'username': score['username'],
            'score': score['score'],
            'upload_time':  uploaded_at_in_bj.strftime("%m-%d %H:%M"),
            'status': score['status'],
            'id': score['id'],
        })

    context = {
        'scores': ranked_users,
    }
    return render(request, 'model_score/submissions.html', context)


def submission_detail_view(request, file_id):
    # 获取对应的记录
    submission = ModelScore.objects.get(id=file_id)
    scores = []
    uploaded_at_in_utc = submission.upload_time
    beijing_tz = pytz.timezone('Asia/Shanghai')
    uploaded_at_in_bj = uploaded_at_in_utc.astimezone(beijing_tz)
    score = {
        'username': submission.username,
        'score': submission.score,
        'upload_time':  uploaded_at_in_bj.strftime("%m-%d %H:%M"),
        'status': submission.status,
    }
    scores.append(score)
    context = {
        'scores': scores,
    }
    return render(request, 'model_score/submission_detail.html', context)
