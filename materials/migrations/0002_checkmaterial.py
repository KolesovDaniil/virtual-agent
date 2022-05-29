# Generated by Django 4.0.4 on 2022-05-29 10:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('materials', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CheckMaterial',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('is_checked', models.BooleanField(default=False)),
                ('material', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='materials_checks', to='materials.material')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='materials_checks', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'material')},
            },
        ),
    ]
