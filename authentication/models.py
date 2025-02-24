from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator
from django.utils import timezone

class UserProfile(models.Model):
    # 定义会员类型
    MEMBERSHIP_CHOICES = [
        (0, 'Non-Paid User'),
        (1, 'Monthly Paid User'),
        (2, 'Annually Paid User'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    avatar_path = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    default = models.BooleanField(default=False)  # 是否默认同意付费，无需再次提示
    investment_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MaxValueValidator(1000000000)]
    )  # 投资金额（可为空）
    goal = models.CharField(max_length=15, null=True, blank=True, default="")
    
    # 新增字段
    member = models.IntegerField(choices=MEMBERSHIP_CHOICES, default=1)  # 会员类型，默认为按月付费用户
    member_start = models.DateTimeField(null=True, blank=True)  # 会员开始时间
    # 新增字段
    customer_id = models.CharField(max_length=255, blank=True, null=True)  # Stripe Customer ID
    is_cancelled = models.BooleanField(default=False)  # 新增字段，表示是否取消了下一次订阅
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

    def save(self, *args, **kwargs):
        if not self.member_start:
            # 仅保留日期部分，并将时间部分设置为00:00:00
            self.member_start = timezone.now().date()  # 获取当前日期，时分秒部分为00:00:00
        super().save(*args, **kwargs)
