# Generated by Django 4.0.4 on 2022-05-29 17:48

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Material',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=128)),
                ('type', models.CharField(choices=[('quiz', 'Квиз'), ('page', 'Текст'), ('pdf', 'PDF'), ('pptx', 'Презентация'), ('mp4', 'Видео'), ('other', 'Другое')], max_length=32)),
                ('moodle_id', models.IntegerField()),
                ('url', models.URLField()),
                ('deadline', models.DateTimeField(blank=True, null=True)),
                ('module', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='materials', to='courses.module')),
            ],
        ),
        migrations.CreateModel(
            name='CheckMaterial',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('is_checked', models.BooleanField(default=False)),
                ('material', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='materials_checks', to='materials.material')),
            ],
        ),
    ]
