# Generated by Django 4.2.17 on 2024-12-28 13:06

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Eleves',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=30)),
                ('post_nom', models.CharField(max_length=30)),
                ('pre_nom', models.CharField(max_length=30)),
            ],
        ),
    ]
