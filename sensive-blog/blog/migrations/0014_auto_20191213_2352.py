# Generated by Django 3.0 on 2019-12-13 20:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0013_auto_20191130_1633'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='post_comments', to='blog.Post', verbose_name='Пост, к которому написан'),
        ),
    ]
