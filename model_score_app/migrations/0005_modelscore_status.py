# Generated by Django 5.0.1 on 2024-01-21 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('model_score_app', '0004_fileupload'),
    ]

    operations = [
        migrations.AddField(
            model_name='modelscore',
            name='status',
            field=models.CharField(default='default_status', max_length=200),
        ),
    ]