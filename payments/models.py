from django.db import models
from django.contrib.auth.models import User

class Payment_history(models.Model):  # 模型名称为 Payment_history
    PAYMENT_TYPES = [
        ('add_funds', 'Add Funds'),
        ('member_fee', 'Member Fee'),
        ('purchase_report', 'Purchase Report'),
        ('refund', 'Refund'),
    ]

    PAYMENT_METHODS = [
        ('credit_card', 'Credit Card'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Bank Transfer'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_history', verbose_name='用户')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='付款金额')
    time = models.TimeField(verbose_name='付款时间')
    date = models.DateField(verbose_name='付款日期')
    method = models.CharField(max_length=20, choices=PAYMENT_METHODS, verbose_name='付款方式')
    type = models.CharField(max_length=20, choices=PAYMENT_TYPES, verbose_name='用途')

    def __str__(self):
        return f"{self.user.username} - {self.type} - {self.amount} on {self.date}"

    class Meta:
        verbose_name = '付款记录'
        verbose_name_plural = '付款记录'
        ordering = ['-date', '-time']


class Payment_methd(models.Model):  # 使用您指定的模型名称
    PAYMENT_METHODS = [
        ('credit_card', 'Credit Card'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Bank Transfer'),
        ('stripe', 'Stripe'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_methods', verbose_name='用户')
    method = models.CharField(max_length=20, choices=PAYMENT_METHODS, verbose_name='支付方式')
    stripe_payment_method_id = models.CharField(max_length=255, null=True, blank=True, verbose_name='Stripe Payment Method ID')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    def __str__(self):
        return f"{self.user.username} - {self.method}"

    class Meta:
        verbose_name = '支付方式'
        verbose_name_plural = '支付方式'