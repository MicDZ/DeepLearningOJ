from django.contrib.auth.models import User
from django.db import models
import uuid
class ModelScore(models.Model):
    username = models.CharField(max_length=200,default='default_username')
    score = models.FloatField(default=0.0)
    # 0-9每一类的准确率，存十个浮点数
    class0 = models.FloatField(default=0.0)
    class1 = models.FloatField(default=0.0)
    class2 = models.FloatField(default=0.0)
    class3 = models.FloatField(default=0.0)
    class4 = models.FloatField(default=0.0)
    class5 = models.FloatField(default=0.0)
    class6 = models.FloatField(default=0.0)
    class7 = models.FloatField(default=0.0)
    class8 = models.FloatField(default=0.0)
    class9 = models.FloatField(default=0.0)

    upload_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=200,default='default_status')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(upload_to='model_files', default='default_file')
    def __str__(self):
        return f"{self.user.username}'s Model Score: {self.score} ({self.upload_time})"


class User(models.Model):
    # username 使用uft-8编码，最大长度为200
    username = models.CharField(max_length=200,default='default_username')
    password = models.CharField(max_length=200,default='default_password')
    token = models.CharField(max_length=200,default='default_token')
    def __str__(self):
        return f"{self.username}'s password: {self.password}"
