from django.db import models
from property.models import Property
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User

class Holding(models.Model):
    BID_STATUS_CHOICES = [
        ('Bid', 'Bid'),
        ('Won', 'Won'),
        ('Foreclosed', 'Foreclosed'),
        ('Archived', 'Archived'),
    ]
    
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='holdings')  # 引用 Property 表
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='holdings')  # 引用 User 表
    my_bid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # 竞标金额（美元）
    my_bid_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # 竞标百分比
    status = models.CharField(max_length=20, choices=BID_STATUS_CHOICES)
    note = models.TextField(max_length=50, blank=True)  # 备注，最多50个字符

    def __str__(self):
        return f"{self.property.name} - {self.status} - {self.user.username}"

    class Meta:
        verbose_name = 'Holding'
        verbose_name_plural = 'Holdings'




class UserInput(models.Model):
    
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='user_inputs')  # 引用 Property 表
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_inputs')  # 引用 User 表
    street_address = models.CharField(max_length=255, blank=True)  # 完整地址
    auction_authority = models.CharField(max_length=255, blank=True)  # 拍卖方
    state = models.CharField(max_length=50, blank=True)  # 所属州
    amount_in_sale = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)  # 售卖金额
    deposit_deadline = models.DateField(null=True, blank=True)  # 定金截止日期
    auction_start = models.DateField(null=True, blank=True)  # 拍卖开始日期
    auction_end = models.DateField(null=True, blank=True)  # 拍卖结束日期
    city = models.CharField(max_length=100)
    zip = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.property.name} - {self.user.username}"

    class Meta:
        verbose_name = 'User Input'
        verbose_name_plural = 'User Inputs'