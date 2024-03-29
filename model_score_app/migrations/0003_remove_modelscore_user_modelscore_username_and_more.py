# Generated by Django 5.0.1 on 2024-01-21 04:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('model_score_app', '0002_modelscore_delete_filescore'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='modelscore',
            name='user',
        ),
        migrations.AddField(
            model_name='modelscore',
            name='username',
            field=models.CharField(default='default_username', max_length=200),
        ),
        migrations.AlterField(
            model_name='modelscore',
            name='score',
            field=models.FloatField(default=0.0),
        ),
    ]
