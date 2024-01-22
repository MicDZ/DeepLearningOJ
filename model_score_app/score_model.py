import os
import torch
import string
import time
from celery import shared_task
from .models import ModelScore, FileUpload


@shared_task(bind=True)
def score_model(self, file_id):
    # 你的模型代码根据pt文件中1的个数来打分
    # 读取模型
    # model = torch.load(model_file)
    model_file = ModelScore.objects.get(id=file_id).file
    print(model_file)
    # 计算i的个数
    count = 0
    #     with open(model_file, 'r') as f:
    #         for line in f:
    #             count += line.count('i')
    # 等待十秒
    time.sleep(10)
    model_content = str(model_file.read())
    print(model_content)
    # 遍历所有字符
    for char in model_content:
        # 如果是i，计数器加1
        if char == 'i':
            count += 1
        print(count)
    # 返回分数
    ModelScore.objects.filter(id=file_id).update(score=count, status='Success')
    return
