# Generated by Django 5.0.1 on 2024-01-21 13:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('model_score_app', '0006_alter_modelscore_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='modelscore',
            name='file',
            field=models.FileField(default='default_file', upload_to='model_files'),
        ),
    ]
