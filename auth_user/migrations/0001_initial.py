# Generated by Django 4.0.4 on 2022-05-14 21:45

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
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gender', models.CharField(choices=[('', 'Please select'), ('M', 'Men'), ('F', 'Woman'), ('O', 'Other'), ('N', 'Rather not Say')], max_length=1)),
                ('birthday', models.DateField()),
                ('entry_date', models.DateField(auto_now_add=True)),
                ('block_coin', models.IntegerField(default=0)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]