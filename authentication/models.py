from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator

class UserProfile(models.Model):
    GOAL_CHOICES = [
        ('interest', 'Interest'),
        ('foreclosure', 'Foreclosure'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")  # 关联 User 表
    avatar_path = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)  # 名（可为空）
    last_name = models.CharField(max_length=50, blank=True, null=True)  # 姓（可为空）
    phone_number = models.CharField(max_length=15, blank=True, null=True)  # 手机号码（可为空）
    default = models.BooleanField(default=False)  # 是否默认同意付费，无需再次提示s
    investment_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MaxValueValidator(1000000000)]
    ) # 投资金额（可为空）
    goal = models.CharField(
        max_length=15, choices=GOAL_CHOICES, null=True, blank=True, default=""
    )
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
