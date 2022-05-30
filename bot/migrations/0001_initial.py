# Generated by Django 4.0.4 on 2022-05-30 11:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserState',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.IntegerField(choices=[(1, 'FAQ номер курса'), (2, 'FAQ номер вопроса'), (3, 'Дедлайны номер курса')])),
                ('object_uuid', models.CharField(max_length=64, null=True)),
                ('is_actual', models.BooleanField(default=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='states', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
