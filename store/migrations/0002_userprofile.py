from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id',         models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('avatar',     models.ImageField(blank=True, null=True, upload_to='avatars/')),
                ('phone',      models.CharField(blank=True, max_length=20)),
                ('address',    models.TextField(blank=True)),
                ('city',       models.CharField(blank=True, max_length=100)),
                ('country',    models.CharField(blank=True, max_length=100)),
                ('bio',        models.TextField(blank=True, max_length=300)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='profile',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
        ),
    ]
