# Generated by Django 3.0.7 on 2020-06-24 22:33

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('Doctors', '0007_auto_20200624_0057'),
    ]

    operations = [
        migrations.AddField(
            model_name='userbook',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]