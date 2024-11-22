from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    GOAL_CHOICES = [
        ('interest', 'Interest'),
        ('foreclosure', 'Foreclosure'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")  # 关联 User 表
    first_name = models.CharField(max_length=50, blank=True, null=True)  # 名（可为空）
    last_name = models.CharField(max_length=50, blank=True, null=True)  # 姓（可为空）
    phone_number = models.CharField(max_length=15, blank=True, null=True)  # 手机号码（可为空）
    investment_amount = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True
    )  # 投资金额（可为空）
    goal = models.CharField(
        max_length=15, choices=GOAL_CHOICES, null=True, blank=True, default=""
    )
    def __str__(self):
        return f"{self.user.username}'s Profile"
