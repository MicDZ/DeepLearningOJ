# model_score_app/views.py
import json

from django.shortcuts import render, redirect
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib import messages
from django.http import HttpResponseBadRequest
from .score_model import score_model
from .models import ModelScore, FileUpload, User
from django.db.models import Max
import uuid
from django.utils import timezone
import pytz
from django.http import JsonResponse
from django.http import HttpResponse
import urllib.parse
def upload_view(request):
    # 从cookies中读取token
    token = request.COOKIES.get('token')
    # 如果token不存在，则返回错误信息
    if not token or not User.objects.filter(token=token).exists():
        # 重定向到登录页面
        return redirect('login_view')
    print("Login token by "+token)
    # 生成一个新的文件id
    file_id = str(uuid.uuid4())
    if request.method == 'POST':
        # 判断是否是upload请求
        action = request.POST.get('action')
        if action == 'upload':

            # 从数据库获取姓名
            username = User.objects.get(token=token).username
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
    # 获取当前时间，若与上传时间相差超过1分钟，则认为评分超时
    now = timezone.now()
    if now - uploaded_at_in_utc > timezone.timedelta(minutes=1) and submission.status == 'Running':
        submission.status = 'Unknown Error'
        submission.save()
        ModelScore.objects.filter(id=file_id).update(status='Unknown Error')

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

def login_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action != 'login':
            return render(request, 'model_score/login.html')
        # 获取姓名
        username = request.POST.get('username')
        password = request.POST.get('password')
        if not username:
            return
        if not password:
            return
        if User.objects.filter(username=username, password=password).exists():
            # 如果记录已存在，生成token
            token = str(uuid.uuid4())
            # 将token存入数据库
            User.objects.filter(username=username).update(token=token)
            # 返回token
            response = render(request,'model_score/upload.html', {'username': username})
            response.set_cookie('token', token)
            username_encoded = json.dumps(username)
            response.set_cookie('username', username_encoded)
            return response
        else:
            # 存储用户信息
            # user = User(username=username, password=password)
            # user.save()

            return render(request, 'model_score/login.html', {'error_message': '登录失败，请检查用户名和密码是否正确'})

    return render(request, 'model_score/login.html')
