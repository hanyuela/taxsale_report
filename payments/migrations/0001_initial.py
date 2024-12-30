# Generated by Django 4.2 on 2024-12-30 08:47

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
            name='Payment_history',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='付款金额')),
                ('time', models.TimeField(verbose_name='付款时间')),
                ('date', models.DateField(verbose_name='付款日期')),
                ('method', models.CharField(choices=[('credit_card', 'Credit Card'), ('paypal', 'PayPal'), ('bank_transfer', 'Bank Transfer'), ('other', 'Other')], max_length=20, verbose_name='付款方式')),
                ('type', models.CharField(choices=[('add_funds', 'Add Funds'), ('member_fee', 'Member Fee'), ('purchase_report', 'Purchase Report'), ('refund', 'Refund')], max_length=20, verbose_name='用途')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payment_history', to=settings.AUTH_USER_MODEL, verbose_name='用户')),
            ],
            options={
                'verbose_name': '付款记录',
                'verbose_name_plural': '付款记录',
                'ordering': ['-date', '-time'],
            },
        ),
    ]