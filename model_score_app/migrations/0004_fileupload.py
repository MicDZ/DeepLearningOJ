# Generated by Django 5.0.1 on 2024-01-21 06:49

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('model_score_app', '0003_remove_modelscore_user_modelscore_username_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='FileUpload',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('file', models.FileField(upload_to='model_files')),
                ('upload_time', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]