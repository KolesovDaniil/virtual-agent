# Generated by Django 4.0.4 on 2022-05-22 15:32

from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=256)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='groups', to='courses.course')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, to=settings.AUTH_USER_MODEL)),
                ('uuid', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('position', models.IntegerField(blank=True, choices=[(1, 'Лаборант'), (2, 'Старший лаборант'), (3, 'Ассистент'), (4, 'Преподаватель'), (5, 'Старший преподаватель'), (6, 'Доцент'), (7, 'Профессор'), (8, 'Завкафедрой'), (9, 'Декан'), (10, 'Проректор'), (11, 'Ректор')], null=True, verbose_name='Должность')),
                ('image', models.URLField(blank=True, null=True, verbose_name='Аватарка')),
                ('type', models.IntegerField(choices=[(1, 'Студент'), (2, 'Преподаватель')])),
                ('group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='students', to='users.group', verbose_name='Группа')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
