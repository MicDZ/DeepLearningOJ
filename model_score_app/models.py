from django.contrib.auth.models import User
from django.db import models
import uuid
class ModelScore(models.Model):
    username = models.CharField(max_length=200,default='default_username')
    score = models.FloatField(default=0.0)
    upload_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=200,default='default_status')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(upload_to='model_files', default='default_file')
    def __str__(self):
        return f"{self.user.username}'s Model Score: {self.score} ({self.upload_time})"

class FileUpload(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(upload_to='model_files')
    upload_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file.name} ({self.upload_time})"

class User(models.Model):
    # username 使用uft-8编码，最大长度为200
    username = models.CharField(max_length=200,default='default_username')
    password = models.CharField(max_length=200,default='default_password')
    token = models.CharField(max_length=200,default='default_token')
    def __str__(self):
        return f"{self.username}'s password: {self.password}"