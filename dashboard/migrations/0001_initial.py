# Generated by Django 4.2.5 on 2025-02-02 23:48

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(max_length=500)),
                ('label', models.CharField(choices=[('In Progress', 'In Progress'), ('Pending', 'Pending'), ('Done', 'Done'), ('Archived', 'Archived')], default='Pending', max_length=11)),
                ('created', models.DateField(auto_now_add=True)),
                ('deadline', models.DateField()),
            ],
        ),
    ]
